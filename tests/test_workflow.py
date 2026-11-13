import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location('workflow', Path(__file__).resolve().parents[1] / 'scripts/workflow.py')
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.old_home = w.HOME
        w.HOME = self.root / 'environment'
        verification = self.root / 'environment-report.md'
        verification.write_text('Mock environment verification for unit tests only.')
        for name in w.environment.REQUIRED:
            version = '22.0.0' if name == 'node' else '3.11.0'
            w.environment.verify(w.HOME, w.save, name, verification, version, 'ready', verification)
        self.image = self.root / 'image.png'
        self.image.write_bytes(b'test fixture')
        self.project = self.root / 'project'
        w.init(self.project, self.image)
        self.evidence = self.root / 'report.md'
        self.evidence.write_text('Test evidence only; not a real avatar acceptance.')

    def tearDown(self):
        w.HOME = self.old_home
        self.temp.cleanup()

    def test_resume_cannot_overwrite(self):
        with self.assertRaises(ValueError):
            w.init(self.project, self.image)
        self.assertEqual(w.load(self.project)['input_sha256'], w.sha(self.image))

    def test_duplicate_paid_intent_is_blocked(self):
        w.task(self.project, 'head-01', 'intent', cost=10)
        w.task(self.project, 'head-01', 'unknown')
        with self.assertRaises(ValueError):
            w.task(self.project, 'head-01', 'intent')
        self.assertFalse(w.readiness(w.load(self.project))['ready'])

    def test_task_requires_intent_and_real_url(self):
        with self.assertRaises(ValueError):
            w.task(self.project, 'head', 'submitted', url='https://studio.tripo3d.ai/task/1')
        w.task(self.project, 'head', 'intent')
        with self.assertRaises(ValueError):
            w.task(self.project, 'head', 'submitted')
        w.task(self.project, 'head', 'submitted', url='https://studio.tripo3d.ai/task/1')
        w.task(self.project, 'head', 'completed')
        self.assertEqual(w.load(self.project)['tasks']['head']['status'], 'completed')

    def test_live_capture_is_required(self):
        for c in w.CHECKS:
            if c != 'live_capture':
                w.record(self.project, c, 'pass', self.evidence)
        self.assertFalse(w.readiness(w.load(self.project))['ready'])
        with self.assertRaises(ValueError):
            w.record(self.project, 'live_capture', 'not_applicable', self.evidence)
        w.record(self.project, 'live_capture', 'pass', self.evidence)
        self.assertTrue(w.readiness(w.load(self.project))['ready'])
        self.evidence.write_text('changed report')
        self.assertFalse(w.readiness(w.load(self.project))['ready'])

    def test_blocker_still_prevents_readiness(self):
        for c in w.CHECKS:
            w.record(self.project, c, 'pass', self.evidence)
        s = w.load(self.project); s['blocker'] = {'reason': 'insufficient_credits'}
        self.assertFalse(w.readiness(s)['ready'])

    def test_platform_assets(self):
        self.assertEqual(w.platform_key('Darwin', 'arm64'), 'darwin-arm64')
        self.assertEqual(w.platform_key('Windows', 'AMD64'), 'windows-x64')
        for key in ('darwin-arm64', 'darwin-x64', 'windows-x64', 'linux-x64'):
            self.assertTrue(w.resolve('xr-animator', key)[1]['sha256'])
        with self.assertRaises(ValueError):
            w.resolve('xr-animator', 'linux-arm64')
        self.assertEqual(set(w.deps()), {'charakuru', 'xr-animator'})

    def test_archive_path_traversal_rejected(self):
        for name in ('../escape', '/absolute', 'C:/absolute', '..\\escape'):
            b = io.BytesIO()
            with zipfile.ZipFile(b, 'w') as z:
                z.writestr(name, 'bad')
            b.seek(0)
            with zipfile.ZipFile(b) as z, self.assertRaises(ValueError):
                w.validate_zip(z)

    def test_escaping_symlink_rejected(self):
        b = io.BytesIO()
        with zipfile.ZipFile(b, 'w') as z:
            i = zipfile.ZipInfo('link'); i.external_attr = 0o120777 << 16
            z.writestr(i, '../../escape')
        b.seek(0)
        with zipfile.ZipFile(b) as z, self.assertRaises(ValueError):
            w.validate_zip(z)


if __name__ == '__main__':
    unittest.main()
