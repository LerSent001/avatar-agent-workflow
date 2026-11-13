"""Offline CLI walkthrough using text fixtures, not generated media/models."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FirstRunTests(unittest.TestCase):
    def test_new_user_cli_flow_with_spaces_and_resume(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'project space'
            root.mkdir()
            home = root / 'runtime'
            env = {**os.environ, 'AVATAR_WORKFLOW_HOME': str(home)}
            project = root / 'character'
            report = root / 'test report.md'
            report.write_text('OFFLINE MOCK: not actual user approval or model acceptance.', encoding='utf-8')
            image = root / 'reference.png'; image.write_bytes(b'offline reference fixture')

            def call(*args, expected=0):
                r = subprocess.run([sys.executable, str(ROOT / 'scripts/workflow.py'), *map(str, args)],
                                   cwd=ROOT, env=env, capture_output=True, text=True, timeout=15)
                self.assertEqual(r.returncode, expected, (args, r.stderr))
                return json.loads(r.stdout) if r.returncode == 0 else None

            call('init', project, '--image', image)
            call('install', 'charakuru', expected=1)
            call('task', project, 'head', 'intent', expected=1)
            for name in ('python', 'node', 'blender', 'vrm-addon', 'charakuru', 'xr-animator', 'browser', 'blender-control'):
                version = {'node': '22.0.0', 'blender': '5.2.3'}.get(name, '3.11.0')
                call('verify-dependency', name, '--path', report, '--version', version, '--status', 'ready', '--evidence', report)
            call('references', project, image)
            call('task', project, 'head', 'intent', expected=1)
            call('check', project, 'reference', 'pass', '--evidence', report)
            call('block', project, 'insufficient_credits')
            call('task', project, 'head', 'intent', expected=1)
            self.assertEqual(call('status', project)['blocker']['reason'], 'insufficient_credits')
            call('block', project, 'clear')
            # Local bookkeeping only; these commands never submit jobs to Tripo.
            call('task', project, 'head', 'intent')
            call('task', project, 'head', 'failed')
            call('resolve-task', project, 'head', '--evidence', report)
            call('task', project, 'head-retry', 'intent')
            call('task', project, 'head-retry', 'submitted', '--url', 'https://studio.tripo3d.ai/task/offline-fixture')
            call('task', project, 'head-retry', 'completed')
            vrm = root / 'avatar.vrm'; vrm.write_bytes(b'offline model placeholder')
            blend = root / 'avatar.blend'; blend.write_bytes(b'offline source placeholder')
            call('model', project, '--vrm', vrm, '--source', blend)
            for check in ('environment', 'geometry', 'rig', 'expressions', 'springs', 'export_reimport', 'xr_loaded'):
                call('check', project, check, 'pass', '--evidence', report)
            call('ready', project, expected=2)
            call('check', project, 'live_capture', 'pass', '--evidence', report)
            self.assertTrue(call('ready', project)['ready'])
            output = root / 'delivery'
            call('deliver', project, '--output', output, '--name', 'Offline test', '--author', 'Test', '--usage', 'Test fixture only')
            manifest = json.loads((output / 'manifest.json').read_text())
            self.assertTrue(all((output / item['path']).is_file() for item in manifest['files']))
            vrm.write_bytes(b'modified offline placeholder')
            call('ready', project, expected=2)


if __name__ == '__main__':
    unittest.main()
