import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('workflow_env_test', Path(__file__).resolve().parents[1] / 'scripts/workflow.py')
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)
e = w.environment


class EnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.previous_home = w.HOME
        w.HOME = self.root / 'state'
        self.report = self.root / 'report.md'
        self.report.write_text('Test fixture: verified installed version and enabled plugin.')
        self.approval = self.root / 'approval.md'
        self.approval.write_text('Test fixture: user agrees to install the listed software.')

    def tearDown(self):
        w.HOME = self.previous_home
        self.temp.cleanup()

    def test_install_without_approval_does_not_download(self):
        with patch.object(w, 'download') as download, self.assertRaises(ValueError):
            w.unpack('charakuru')
        download.assert_not_called()

    def test_compatible_existing_dependency_is_reused(self):
        e.verify(w.HOME, w.save, 'charakuru', self.report, '1.1.1', 'ready', self.report)
        with patch.object(w, 'download') as download:
            self.assertEqual(w.unpack('charakuru'), self.report.resolve())
        download.assert_not_called()

    def test_approval_is_scoped_and_install_requires_recheck(self):
        e.approve(w.HOME, w.save, ['blender'], self.approval)
        with self.assertRaises(ValueError):
            e.authorize(w.HOME, w.save, 'vrm-addon')
        self.assertEqual(e.authorize(w.HOME, w.save, 'blender')['action'], 'install')
        self.assertEqual(e.authorize(w.HOME, w.save, 'blender')['action'], 'install')
        with self.assertRaises(ValueError):
            e.require_ready(w.HOME)

    def test_plugin_missing_blocks_environment_and_generation(self):
        for name in e.REQUIRED:
            if name != 'vrm-addon':
                version = '22.0.0' if name == 'node' else '3.11.0'
                e.verify(w.HOME, w.save, name, self.report, version, 'ready', self.report)
        image = self.root / 'image.png'; image.write_bytes(b'fixture')
        project = self.root / 'project'; w.init(project, image)
        with self.assertRaises(ValueError):
            w.record(project, 'environment', 'pass', self.report)
        with self.assertRaises(ValueError):
            w.task(project, 'head', 'intent')
        e.verify(w.HOME, w.save, 'vrm-addon', self.report, 'verified-version', 'ready', self.report)
        w.record(project, 'environment', 'pass', self.report)
        w.task(project, 'head', 'intent')

    def test_incompatible_runtime_cannot_be_ready(self):
        with self.assertRaises(ValueError):
            e.verify(w.HOME, w.save, 'node', self.report, '20.0.0', 'ready', self.report)
        self.assertIsNone(e.compatible('blender', '5.2.3'))

    def test_changed_binary_or_report_invalidates_verification(self):
        binary = self.root / 'binary'; binary.write_bytes(b'v1')
        e.verify(w.HOME, w.save, 'blender', binary, '5.2.3', 'ready', self.report)
        entry = e.read(w.HOME)['dependencies']['blender']
        self.assertTrue(e.valid_entry(entry))
        binary.write_bytes(b'v2')
        self.assertFalse(e.valid_entry(entry))

    def test_changed_approval_cannot_authorize_installation(self):
        e.approve(w.HOME, w.save, ['blender'], self.approval)
        self.approval.write_text('changed')
        with self.assertRaises(ValueError):
            e.authorize(w.HOME, w.save, 'blender')


if __name__ == '__main__':
    unittest.main()
