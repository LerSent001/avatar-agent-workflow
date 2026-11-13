#!/usr/bin/env python3
"""Fetch a pinned workflow on first use; never install modeling dependencies."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tempfile
from urllib.request import Request, urlopen
import zipfile

REVISION = 'c02d5bdc3c9c886e97389e771b0ecd307322b15e'
REPOSITORY = 'LerSent001/avatar-agent-workflow'
FILES = ('AGENTS.md', 'dependencies.json', 'LICENSE', 'THIRD_PARTY_NOTICES.md',
         'scripts/workflow.py', 'scripts/environment.py', 'docs/INSTALL.md',
         'docs/WORKFLOW.md', 'docs/ACCEPTANCE.md', 'docs/TROUBLESHOOTING.md')


def fingerprint(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate(directory):
    receipt = directory / '.workflow-source.json'
    if not receipt.is_file():
        raise ValueError('Workflow directory exists without a source receipt; use another cache directory.')
    info = json.loads(receipt.read_text(encoding='utf-8'))
    if info.get('revision') != REVISION or set(info.get('files', {})) != set(FILES):
        raise ValueError('Workflow source receipt does not match the pinned release.')
    for name in FILES:
        path = directory / name
        if not path.is_file() or path.is_symlink() or fingerprint(path) != info['files'][name]:
            raise ValueError('Cached workflow changed: ' + name + '. Preserve existing projects and inspect before replacing it.')
    return directory


def install_archive(data, destination):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.workflow-', dir=destination.parent))
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            selected = {}
            for entry in archive.infolist():
                parts = PurePosixPath(entry.filename).parts
                if len(parts) < 2:
                    continue
                relative = '/'.join(parts[1:])
                if relative in FILES:
                    if relative in selected or (entry.external_attr >> 16) & 0o170000 == 0o120000:
                        raise ValueError('Invalid workflow archive entry.')
                    if entry.file_size > 2 * 1024 * 1024:
                        raise ValueError('Unexpected workflow source file size.')
                    selected[relative] = entry
            if set(selected) != set(FILES):
                raise ValueError('Archive does not contain the complete workflow.')
            for name, entry in selected.items():
                target = staging / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(entry))
        receipt = {'repository': REPOSITORY, 'revision': REVISION,
                   'files': {name: fingerprint(staging / name) for name in FILES}}
        (staging / '.workflow-source.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
        if destination.exists():
            return validate(destination)
        staging.rename(destination)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return destination


def resolve(cache):
    dest = Path(cache).expanduser().resolve() / REVISION
    if dest.exists():
        return validate(dest)
    url = f'https://codeload.github.com/{REPOSITORY}/zip/{REVISION}'
    with urlopen(Request(url, headers={'User-Agent': 'avatar-character-skill/1.0'}), timeout=45) as response:
        data = response.read(16 * 1024 * 1024 + 1)
    if len(data) > 16 * 1024 * 1024:
        raise ValueError('Workflow archive exceeds the source download limit.')
    return install_archive(data, dest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-dir', default=os.environ.get('AVATAR_WORKFLOW_CACHE', str(Path.home() / '.local/share/avatar-agent-workflow')))
    args = parser.parse_args()
    try:
        path = resolve(args.cache_dir)
        print(json.dumps({'workflow_directory': str(path), 'revision': REVISION,
                          'next': 'Read AGENTS.md in this directory. Ask before installing missing or incompatible dependencies.'}, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
