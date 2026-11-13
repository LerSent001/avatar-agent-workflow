"""Dependency discovery, approval records and environment readiness."""
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

REQUIRED = ('python', 'node', 'blender', 'vrm-addon', 'charakuru', 'xr-animator', 'browser', 'blender-control')


def stamp():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read(home):
    p = Path(home) / 'environment.json'
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else {'dependencies': {}, 'approvals': []}


def version_tuple(text):
    m = re.search(r'(\d+)\.(\d+)(?:\.(\d+))?', text)
    return tuple(int(n or 0) for n in m.groups()) if m else None


def compatible(name, version):
    v = version_tuple(version)
    if not v:
        return None
    if name == 'python':
        return v >= (3, 9, 0)
    if name == 'node':
        return v >= (22, 0, 0)
    if name == 'blender':
        return v[:2] == (5, 2)
    # Other components require checking the selected upstream kit and plugins.
    return None


def candidates(name, home):
    found = []
    override = os.environ.get('AVATAR_' + name.upper().replace('-', '_') + '_PATH')
    if override:
        found.append(Path(override).expanduser())
    commands = {'python': ('python3', 'python'), 'node': ('node',), 'blender': ('blender',),
                'browser': ('google-chrome', 'chromium', 'chromium-browser'),
                'charakuru': (), 'xr-animator': (), 'vrm-addon': (), 'blender-control': ()}
    if name == 'python':
        found.append(Path(sys.executable))
    for command in commands[name]:
        p = shutil.which(command)
        if p:
            found.append(Path(p))
    system = platform.system()
    if system == 'Darwin':
        patterns = {'blender': ('Blender*.app/Contents/MacOS/Blender',),
                    'browser': ('Google Chrome.app', 'Chromium.app', 'Microsoft Edge.app'),
                    'xr-animator': ('XR*/*.app', 'XR*.app', 'XR-Animator/Electron.app')}
        for root in (Path('/Applications'), Path.home() / 'Applications'):
            for pattern in patterns.get(name, ()):
                found.extend(root.glob(pattern))
    elif system == 'Windows':
        for env in ('ProgramFiles', 'ProgramFiles(x86)', 'LOCALAPPDATA'):
            if not os.environ.get(env):
                continue
            root = Path(os.environ[env])
            patterns = {'blender': ('Blender Foundation/Blender */blender.exe',),
                        'node': ('nodejs/node.exe',),
                        'browser': ('Google/Chrome/Application/chrome.exe', 'Microsoft/Edge/Application/msedge.exe')}
            for pattern in patterns.get(name, ()):
                found.extend(root.glob(pattern))
    if name in ('charakuru', 'xr-animator'):
        root = Path(home) / 'tools' / name
        found.extend(p.parent for p in root.glob('*/.workflow-installed.json'))
    return list(dict.fromkeys(str(p.resolve()) for p in found if p.exists()))


def directory_signature(path):
    rows = []
    root = Path(path)
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in ('__pycache__', '.git'))
        for name in sorted(dirs + files):
            p = Path(base) / name
            st = p.lstat()
            rows.append((str(p.relative_to(root)), st.st_size, st.st_mtime_ns,
                         os.readlink(p) if p.is_symlink() else None))
    return hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()


def valid_entry(entry):
    if entry.get('status') != 'ready':
        return False
    p = Path(entry.get('path', ''))
    evidence = Path(entry.get('evidence', ''))
    if not p.exists() or not evidence.is_file():
        return False
    if digest(evidence) != entry.get('evidence_sha256'):
        return False
    if p.is_file() and digest(p) != entry.get('file_sha256'):
        return False
    if p.is_dir() and directory_signature(p) != entry.get('directory_signature'):
        return False
    return True


def inspect(home):
    state = read(home)
    results = {}
    for name in REQUIRED:
        entry = state['dependencies'].get(name, {})
        if valid_entry(entry):
            results[name] = {**entry, 'action': 'reuse'}
            continue
        paths = candidates(name, home)
        if entry.get('path') and Path(entry['path']).exists() and entry['path'] not in paths:
            paths.insert(0, entry['path'])
        result = {'status': 'unverified' if paths else 'not_detected', 'candidates': paths,
                  'action': 'verify_existing' if paths else 'inspect_app_locations_then_request_installation'}
        probes = []
        if name in ('python', 'node', 'blender'):
            for path in paths:
                try:
                    r = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=15)
                    text = r.stdout.strip()
                    check = compatible(name, text) if r.returncode == 0 else None
                    probes.append({'path': path, 'version': text[:200], 'compatible': check})
                except (OSError, subprocess.SubprocessError):
                    probes.append({'path': path, 'compatible': None})
            result['probes'] = probes
            if probes and all(p['compatible'] is False for p in probes):
                result.update(status='incompatible', action='request_upgrade')
        results[name] = result
    return {'dependencies': results, 'ready': all(x['status'] == 'ready' for x in results.values()),
            'next': 'Verify detected versions and plugins. Ask the user before installing or upgrading each missing/incompatible dependency; a single itemized approval may cover several dependencies. Recheck after installation before production.'}


def verify(home, save, name, path, version, status, evidence):
    p, e = Path(path).expanduser().resolve(), Path(evidence).resolve()
    if not p.exists() or not e.is_file():
        raise ValueError('Dependency path and verification report must exist.')
    if not version.strip():
        raise ValueError('Record the detected version or integration identifier.')
    if status == 'ready' and name in ('python', 'node', 'blender') and compatible(name, version) is not True:
        raise ValueError('Detected version does not meet the runtime requirement.')
    s = read(home)
    s['dependencies'][name] = {'path': str(p), 'version': version, 'status': status,
         'evidence': str(e), 'evidence_sha256': digest(e), 'at': stamp(),
         'file_sha256': digest(p) if p.is_file() else None,
         'directory_signature': directory_signature(p) if p.is_dir() else None}
    save(Path(home) / 'environment.json', s)
    return s['dependencies'][name]


def approve(home, save, names, evidence):
    e = Path(evidence).resolve()
    if not e.is_file() or not e.read_text(encoding='utf-8').strip():
        raise ValueError('Save the user installation/upgrade approval before recording it.')
    s = read(home)
    approval = {'names': list(names), 'evidence': str(e), 'sha256': digest(e), 'at': stamp(), 'used': []}
    s['approvals'].append(approval)
    save(Path(home) / 'environment.json', s)
    return approval


def authorize(home, save, name):
    s = read(home)
    entry = s['dependencies'].get(name, {})
    if valid_entry(entry):
        return {'action': 'reuse', 'path': entry['path']}
    for approval in reversed(s['approvals']):
        e = Path(approval['evidence'])
        if name in approval['names'] and (name not in approval['used'] or entry.get('status') == 'pending_verification') and e.is_file() and digest(e) == approval['sha256']:
            if name not in approval['used']:
                approval['used'].append(name)
            s['dependencies'][name] = {**entry, 'status': 'pending_verification'}
            save(Path(home) / 'environment.json', s)
            return {'action': 'install', 'next': 'Install the approved dependency, then verify its version and functionality.'}
    raise ValueError(f'{name}: ask the user for installation/upgrade approval first. Record their response with approve-install. No installation has started.')


def require_ready(home):
    s = read(home)
    pending = [name for name in REQUIRED if not valid_entry(s['dependencies'].get(name, {}))]
    if pending:
        raise ValueError('Environment verification required before production: ' + ', '.join(pending))


def probe_blender(executable):
    code = """import bpy, addon_utils, json
items = []
for module in addon_utils.modules():
    info = getattr(module, 'bl_info', {})
    if 'vrm' in module.__name__.lower() or 'vrm' in info.get('name', '').lower() or 'mcp' in module.__name__.lower():
        items.append({'module': module.__name__, 'version': list(info.get('version', [])), 'enabled': module.__name__ in bpy.context.preferences.addons, 'path': getattr(module, '__file__', None)})
print('AVATAR_ENV_JSON=' + json.dumps({'blender_version': bpy.app.version_string, 'plugins': items}))
"""
    r = subprocess.run([str(executable), '--background', '--disable-autoexec', '--python-exit-code', '1', '--python-expr', code], capture_output=True, text=True, timeout=90)
    if r.returncode != 0:
        raise ValueError('Blender plugin inspection failed; check the selected executable.')
    for line in r.stdout.splitlines():
        if line.startswith('AVATAR_ENV_JSON='):
            return json.loads(line.split('=', 1)[1])
    raise ValueError('Blender did not return a plugin inspection result.')
