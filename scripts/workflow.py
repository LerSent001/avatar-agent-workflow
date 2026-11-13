#!/usr/bin/env python3
"""Local bootstrap, progress ledger and delivery gate. No paid service calls."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from urllib.request import Request, urlopen
import webbrowser
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import environment

ROOT = Path(__file__).resolve().parents[1]
HOME = Path(os.environ.get('AVATAR_WORKFLOW_HOME', str(ROOT / '.local'))).resolve()
CHECKS = ('reference', 'environment', 'geometry', 'rig', 'expressions', 'springs',
          'export_reimport', 'xr_loaded', 'live_capture')
LINKS = {
    'tripo': 'https://studio.tripo3d.ai/',
    'charakuru': 'https://github.com/nanocle/Charakuru/releases',
    'xr-animator': 'https://github.com/ButzYung/SystemAnimatorOnline/releases',
    'blender': 'https://www.blender.org/download/',
    'node': 'https://nodejs.org/en/download',
    'vrm-addon': 'https://github.com/saturday06/VRM-Addon-for-Blender/releases',
}


def now():
    return datetime.now(timezone.utc).isoformat()


def save(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.writing-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def platform_key(system=None, machine=None):
    system = (system or platform.system()).lower()
    machine = (machine or platform.machine()).lower()
    arch = {'aarch64': 'arm64', 'arm64': 'arm64', 'amd64': 'x64', 'x86_64': 'x64'}.get(machine)
    if not arch or system not in ('darwin', 'windows', 'linux'):
        raise ValueError(f'Unsupported platform: {system}/{machine}; consult official downloads.')
    return f'{system}-{arch}'


def deps():
    return {k: v for k, v in json.loads((ROOT / 'dependencies.json').read_text()).items() if isinstance(v, dict) and 'assets' in v}


def resolve(name, key=None):
    d = deps()[name]
    a = d['assets'].get('all') or d['assets'].get(key or platform_key())
    if not a:
        raise ValueError(f'{name}: no verified official package for this architecture.')
    return d, a


def download(name):
    d, a = resolve(name)
    url = a['url']
    if not url.startswith(f"https://github.com/{d['repository']}/releases/download/"):
        raise ValueError('Dependency URL must be an official repository release asset.')
    target = HOME / 'downloads' / a['name']
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        partial = target.with_suffix(target.suffix + '.partial')
        try:
            with urlopen(Request(url, headers={'User-Agent': 'avatar-agent-workflow/0.1'}), timeout=60) as r, partial.open('wb') as f:
                shutil.copyfileobj(r, f)
            digest = sha(partial)
            if a.get('sha256') and digest != a['sha256']:
                raise ValueError('Official release checksum mismatch; package was not installed.')
            os.replace(partial, target)
        finally:
            partial.unlink(missing_ok=True)
    digest = sha(target)
    if a.get('sha256') and digest != a['sha256']:
        raise ValueError('Cached archive checksum mismatch; remove this cache and retry.')
    save(target.with_suffix('.receipt.json'), {'source': url, 'version': d['version'],
         'sha256': digest, 'publisher_digest_verified': bool(a.get('sha256')), 'checked_at': now()})
    return target


def validate_zip(z):
    """Reject absolute/traversal paths and escaping symlinks before extraction."""
    for info in z.infolist():
        p = PurePosixPath(info.filename.replace('\\', '/'))
        if p.is_absolute() or '..' in p.parts or any(':' in s for s in p.parts):
            raise ValueError('Unsafe archive path: ' + info.filename)
        if stat.S_ISLNK(info.external_attr >> 16):
            link = z.read(info).decode('utf-8')
            q = PurePosixPath(link.replace('\\', '/'))
            if q.is_absolute() or any(':' in s for s in q.parts):
                raise ValueError('Unsafe archive symlink')
            depth = len(p.parent.parts)
            for part in q.parts:
                depth += -1 if part == '..' else 0 if part == '.' else 1
                if depth < 0:
                    raise ValueError('Escaping archive symlink')


def unpack(name):
    authorization = environment.authorize(HOME, save, name)
    if authorization["action"] == "reuse":
        return Path(authorization["path"])
    archive = download(name)
    d, _ = resolve(name)
    dest = HOME / 'tools' / name / d['version']
    receipt = dest / '.workflow-installed.json'
    if receipt.exists():
        return dest
    if dest.exists():
        raise ValueError(f'Incomplete installation at {dest}; inspect before retrying.')
    dest.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='install-', dir=dest.parent))
    try:
        with zipfile.ZipFile(archive) as z:
            validate_zip(z)
            if platform.system() == 'Darwin':
                # ditto preserves application symlinks and executable permissions.
                subprocess.run(['/usr/bin/ditto', '-x', '-k', str(archive), str(staging)], check=True)
            else:
                # No bundled symlink packages are supported by this extractor.
                if any(stat.S_ISLNK(i.external_attr >> 16) for i in z.infolist()):
                    raise ValueError('Use the official platform extractor for this symlink archive.')
                z.extractall(staging)
                if platform.system() != 'Windows':
                    for i in z.infolist():
                        mode = (i.external_attr >> 16) & 0o777
                        if mode:
                            (staging / i.filename).chmod(mode)
        save(staging / '.workflow-installed.json', {'archive_sha256': sha(archive), 'installed_at': now(),
             'note': 'Extracted only. Agent must verify launch, plugins, and camera separately.'})
        staging.rename(dest)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return dest


def doctor():
    return {'platform': platform_key(), **environment.inspect(HOME),
            'commands': {
                'blender_plugins': 'probe-blender --path BLENDER_EXECUTABLE',
                'verify': 'verify-dependency NAME --path PATH --version VERSION --status ready --evidence REPORT',
                'approval': 'approve-install NAME [NAME ...] --evidence USER_RESPONSE_FILE',
                'external_install': 'authorize-install NAME',
                'bundled_installer': 'install charakuru | install xr-animator'},
            'verification': 'Check each selected version against the installed Charakuru requirements. Verify VRM add-on version and enabled state in the selected Blender; test the Blender control connection and XR launch. Save actual observations as evidence. Installation approval evidence must contain the user response, not an agent-generated approval.'}


def state_path(project):
    return Path(project).resolve() / 'state.json'


def load(project):
    return json.loads(state_path(project).read_text(encoding='utf-8'))


def init(project, image):
    p = state_path(project)
    if p.exists():
        raise ValueError('Project already exists; use status to resume.')
    image = Path(image).resolve()
    if not image.is_file() or image.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp'):
        raise ValueError('Provide an existing PNG/JPEG/WebP reference image.')
    target = p.parent / 'input' / ('reference' + image.suffix.lower())
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(image, target)
    s = {'schema': 1, 'created_at': now(), 'input': str(target.relative_to(p.parent)),
         'input_sha256': sha(target), 'checks': {}, 'tasks': {}, 'blocker': None, 'history': []}
    save(p, s)
    return s


MODEL_CHECKS = ('geometry', 'rig', 'expressions', 'springs', 'export_reimport', 'xr_loaded', 'live_capture')


def current_model(s):
    model = s.get('model', {})
    for key in ('vrm', 'source'):
        item = model.get(key, {})
        p = Path(item.get('path', ''))
        if not p.is_file() or sha(p) != item.get('sha256'):
            raise ValueError('Register the current VRM and Blender source with model before recording model checks.')
    return model['revision']


def register_model(project, vrm, source):
    s = load(project)
    files = {}
    for key, path, suffix in (('vrm', vrm, '.vrm'), ('source', source, '.blend')):
        p = Path(path).resolve()
        if not p.is_file() or p.suffix.lower() != suffix:
            raise ValueError('Provide existing .vrm and .blend model files.')
        files[key] = {'path': str(p), 'sha256': sha(p)}
    revision = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
    if revision != s.get('model', {}).get('revision'):
        for check in MODEL_CHECKS:
            if check in s['checks']:
                s['checks'][check]['status'] = 'pending'
        s['model'] = {**files, 'revision': revision}
        s['history'].append({'event': 'model', 'revision': revision, 'at': now()})
        save(state_path(project), s)
    return s['model']


def record(project, check, status, evidence):
    s = load(project)
    if check != 'reference' and status in ('pass', 'not_applicable'):
        environment.require_ready(HOME)
    e = Path(evidence).resolve()
    if not e.is_file():
        raise ValueError('Evidence must be an existing report, screenshot, or user test record.')
    if check in ('environment', 'xr_loaded', 'live_capture', 'rig', 'export_reimport') and status == 'not_applicable':
        raise ValueError('This mandatory check cannot be skipped.')
    revision = current_model(s) if check in MODEL_CHECKS and status in ('pass', 'not_applicable') else None
    s['checks'][check] = {'status': status, 'evidence': str(e), 'sha256': sha(e), 'at': now(), 'model_revision': revision}
    s['history'].append({'event': 'check', 'check': check, 'status': status, 'at': now()})
    save(state_path(project), s)
    return s['checks'][check]


def task(project, key, status, url=None, cost=None):
    s = load(project)
    if status == 'intent':
        environment.require_ready(HOME)
        reference = s['checks'].get('reference', {})
        reference_evidence = Path(reference.get('evidence', ''))
        if reference.get('status') != 'pass' or not reference_evidence.is_file() or sha(reference_evidence) != reference.get('sha256'):
            raise ValueError('Confirm the reference views with the user and record reference before model generation.')
        if s.get('blocker'):
            raise ValueError('Resolve the recorded blocker before starting a new task.')
        unresolved = [k for k, v in s['tasks'].items() if v['status'] in ('intent', 'unknown')]
        if unresolved:
            raise ValueError('Resolve existing submission status first: ' + ', '.join(unresolved))
    old = s['tasks'].get(key)
    if old and status == 'intent':
        raise ValueError('Task key exists. Inspect the original task; never resubmit blindly.')
    if not old and status != 'intent':
        raise ValueError('Record an intent before any paid submission.')
    if status in ('submitted', 'completed') and not (url or (old or {}).get('url')):
        raise ValueError('Record the actual task URL after submission.')
    transitions = {
        'intent': ('submitted', 'unknown', 'failed', 'cancelled'),
        'submitted': ('submitted', 'unknown', 'completed', 'failed', 'cancelled'),
        'unknown': ('unknown', 'submitted', 'completed', 'failed', 'cancelled'),
        'completed': ('completed',), 'failed': ('failed',), 'cancelled': ('cancelled',)}
    if old and status not in transitions[old['status']]:
        raise ValueError('Invalid task transition; preserve the original task history.')
    if old and url and old.get('url') and url != old['url']:
        raise ValueError('An existing task URL cannot be replaced; record a separate attempt.')
    entry = dict(old or {})
    entry.update({'status': status, 'updated_at': now()})
    if url:
        if not url.startswith('https://studio.tripo3d.ai/'):
            raise ValueError('Use the actual official Tripo task URL.')
        entry['url'] = url
    if cost is not None:
        if cost < 0:
            raise ValueError('Credit cost cannot be negative.')
        entry['credits'] = cost
    s['tasks'][key] = entry
    s['history'].append({'event': 'task', 'key': key, **entry})
    save(state_path(project), s)
    return entry


def readiness(s):
    missing = []
    try:
        environment.require_ready(HOME)
    except ValueError:
        missing.append('environment_dependencies')
    try:
        revision = current_model(s)
    except ValueError:
        revision = None
        missing.append('current_model')
    for c in CHECKS:
        item = s['checks'].get(c, {})
        allowed = ('pass', 'not_applicable') if c in ('expressions', 'springs') else ('pass',)
        if item.get('status') not in allowed:
            missing.append(c)
            continue
        if c in MODEL_CHECKS and (revision is None or item.get('model_revision') != revision):
            missing.append(c + ': model changed')
            continue
        evidence = Path(item.get('evidence', ''))
        if not evidence.is_file() or sha(evidence) != item.get('sha256'):
            missing.append(c + ': evidence missing or changed')
    unfinished = [k for k, v in s['tasks'].items() if v['status'] not in ('completed', 'cancelled')]
    return {'ready': not missing and not unfinished and s.get('blocker') is None,
            'missing_checks': missing, 'unfinished_tasks': unfinished, 'blocker': s.get('blocker'),
            'note': 'Recorded evidence must be reviewed by the Agent. This gate does not judge image quality or prove live capture by itself.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor')
    p = sub.add_parser('probe-blender'); p.add_argument('--path', required=True)
    p = sub.add_parser('verify-dependency'); p.add_argument('name', choices=environment.REQUIRED)
    p.add_argument('--path', required=True); p.add_argument('--version', required=True)
    p.add_argument('--status', choices=('ready', 'incompatible', 'unverified'), required=True)
    p.add_argument('--evidence', required=True)
    p = sub.add_parser('approve-install'); p.add_argument('names', nargs='+', choices=environment.REQUIRED)
    p.add_argument('--evidence', required=True)
    p = sub.add_parser('authorize-install'); p.add_argument('name', choices=environment.REQUIRED)
    for cmd in ('download', 'install'):
        p = sub.add_parser(cmd); p.add_argument('name', choices=tuple(deps()))
    p = sub.add_parser('open'); p.add_argument('service', choices=tuple(LINKS))
    p = sub.add_parser('model'); p.add_argument('project'); p.add_argument('--vrm', required=True); p.add_argument('--source', required=True)
    p = sub.add_parser('init'); p.add_argument('project'); p.add_argument('--image', required=True)
    for cmd in ('status', 'ready'):
        p = sub.add_parser(cmd); p.add_argument('project')
    p = sub.add_parser('check'); p.add_argument('project'); p.add_argument('name', choices=CHECKS)
    p.add_argument('status', choices=('pass', 'fail', 'pending', 'not_applicable')); p.add_argument('--evidence', required=True)
    p = sub.add_parser('task'); p.add_argument('project'); p.add_argument('key')
    p.add_argument('status', choices=('intent', 'submitted', 'unknown', 'completed', 'failed', 'cancelled'))
    p.add_argument('--url'); p.add_argument('--credits', type=int)
    p = sub.add_parser('block'); p.add_argument('project'); p.add_argument('reason', choices=(
        'login_required', 'insufficient_credits', 'balance_unknown', 'permission_required', 'capability_missing', 'clear'))
    p.add_argument('--note', default='')
    a = parser.parse_args()
    try:
        if a.command == 'doctor': result = doctor()
        elif a.command == 'probe-blender': result = environment.probe_blender(a.path)
        elif a.command == 'verify-dependency': result = environment.verify(HOME, save, a.name, a.path, a.version, a.status, a.evidence)
        elif a.command == 'approve-install': result = environment.approve(HOME, save, a.names, a.evidence)
        elif a.command == 'authorize-install': result = environment.authorize(HOME, save, a.name)
        elif a.command == 'download': result = {'archive': str(download(a.name))}
        elif a.command == 'install': result = {'directory': str(unpack(a.name)), 'next': 'Follow docs/INSTALL.md; verify launch.'}
        elif a.command == 'open': result = {'url': LINKS[a.service], 'opened': webbrowser.open(LINKS[a.service])}
        elif a.command == 'model': result = register_model(a.project, a.vrm, a.source)
        elif a.command == 'init': result = init(a.project, a.image)
        elif a.command == 'status': result = load(a.project)
        elif a.command == 'ready': result = readiness(load(a.project))
        elif a.command == 'check': result = record(a.project, a.name, a.status, a.evidence)
        elif a.command == 'task': result = task(a.project, a.key, a.status, a.url, a.credits)
        elif a.command == 'block':
            s = load(a.project)
            s['blocker'] = None if a.reason == 'clear' else {'reason': a.reason, 'note': a.note, 'at': now()}
            s['history'].append({'event': 'blocker', 'value': s['blocker'], 'at': now()})
            save(state_path(a.project), s); result = s['blocker']
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if a.command == 'ready' and not result['ready']:
            return 2
        return 0
    except (ValueError, OSError, KeyError, zipfile.BadZipFile, subprocess.SubprocessError) as e:
        print(str(e), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
