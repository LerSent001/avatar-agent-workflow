#!/usr/bin/env python3
"""Install the lightweight avatar-character skill without fetching dependencies."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
NAME = 'avatar-character'
SOURCE = ROOT / 'skills' / NAME
FILES = ('SKILL.md', 'agents/openai.yaml', 'scripts/resolve_workflow.py', 'LICENSE')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def install(destination):
    parent = Path(destination).expanduser().resolve()
    target = parent / NAME
    if target.is_symlink():
        raise ValueError('A symlinked skill already exists; inspect it before installing.')
    if target.exists():
        if target.is_dir() and all((target / name).is_file() and digest(target / name) == digest(SOURCE / name) for name in FILES):
            return {'status': 'already_installed', 'path': str(target)}
        raise ValueError('A different avatar-character skill exists; preserve it and review the update first.')
    parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.avatar-character-', dir=parent))
    try:
        for name in FILES:
            source = SOURCE / name
            if not source.is_file() or source.is_symlink():
                raise ValueError('Incomplete skill source: ' + name)
            p = staging / name
            p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, p)
        staging.rename(target)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return {'status': 'installed', 'path': str(target), 'next': 'Send a character image and ask to make a character. Refresh the host skill list if needed.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', required=True, help='The current Agent host user skill directory')
    args = parser.parse_args()
    try:
        print(json.dumps(install(args.dest), ensure_ascii=False, indent=2))
    except (OSError, ValueError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
