import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


installer = module('skill_install', ROOT / 'scripts/install_skill.py')
resolver = module('skill_resolver', ROOT / 'skills/avatar-character/scripts/resolve_workflow.py')


class SkillInstallTests(unittest.TestCase):
    def test_install_only_copies_skill_files_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp, patch('urllib.request.urlopen', side_effect=AssertionError('No network during installation')):
            result = installer.install(tmp)
            dest = Path(result['path'])
            self.assertEqual({str(p.relative_to(dest)) for p in dest.rglob('*') if p.is_file()}, set(installer.FILES))
            self.assertEqual(installer.install(tmp)['status'], 'already_installed')
            self.assertFalse((dest / '.local').exists())

    def test_existing_user_changes_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(installer.install(tmp)['path'])
            (dest / 'SKILL.md').write_text('User customization')
            with self.assertRaises(ValueError):
                installer.install(tmp)
            self.assertEqual((dest / 'SKILL.md').read_text(), 'User customization')

    def archive(self, names=None):
        b = io.BytesIO()
        with zipfile.ZipFile(b, 'w') as z:
            for name in (names if names is not None else resolver.FILES):
                z.writestr('repository/' + name, 'fixture: ' + name)
            z.writestr('repository/.local/private.txt', 'excluded')
            z.writestr('repository/../../escape.txt', 'excluded')
        return b.getvalue()

    def test_first_use_selects_only_workflow_sources_and_reuses_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / resolver.REVISION
            resolver.install_archive(self.archive(), dest)
            self.assertFalse((dest / '.local').exists())
            with patch.object(resolver, 'urlopen', side_effect=AssertionError('Cache must not redownload')):
                self.assertEqual(resolver.resolve(tmp), dest.resolve())
            self.assertFalse((Path(tmp).parent / 'escape.txt').exists())

    def test_modified_workflow_is_not_silently_replaced(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / resolver.REVISION
            resolver.install_archive(self.archive(), dest)
            (dest / 'AGENTS.md').write_text('modified')
            with patch.object(resolver, 'urlopen', side_effect=AssertionError('No network')), self.assertRaises(ValueError):
                resolver.resolve(tmp)
            self.assertEqual((dest / 'AGENTS.md').read_text(), 'modified')

    def test_incomplete_download_does_not_leave_installation(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / resolver.REVISION
            with self.assertRaises(ValueError):
                resolver.install_archive(self.archive(resolver.FILES[:-1]), dest)
            self.assertFalse(dest.exists())


if __name__ == '__main__':
    unittest.main()
