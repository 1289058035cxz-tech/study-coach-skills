"""Behavior checks use temporary directories and synthetic data exclusively."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
STATE_SCRIPT = ROOT / 'skills/semester-study-coach/scripts/study_state.py'
INSTALL_SCRIPT = ROOT / 'scripts/install.py'


def run(*args):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')
    return subprocess.run([sys.executable, *map(str, args)],
                          capture_output=True, text=True, encoding='utf-8', env=env)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.state = self.base / 'private-state'
        self.notes = self.base / 'synthetic-notes'

    def command(self, *args):
        return run(STATE_SCRIPT, '--state-dir', self.state, *args)

    def initialize(self, *extra):
        return self.command('init', '--week1-start', '2024-09-02',
                            '--total-weeks', '16', '--timezone', 'Asia/Shanghai',
                            '--vault-root', self.notes, *extra)

    def assertSuccess(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_first_use_and_week_arithmetic(self):
        self.assertSuccess(self.initialize())
        self.assertFalse(self.notes.exists())
        registry = json.loads((self.state / 'subjects.json').read_text())
        self.assertEqual(registry['subjects'], [])
        self.assertFalse((self.state / 'subjects').exists())
        status = self.assertSuccess(self.command('status', '--today', '2024-09-09'))
        self.assertEqual(status['week'], 2)
        self.assertEqual(status['estimated_term_end'], '2024-12-22')

    def test_missing_configuration_is_actionable(self):
        result = self.command('status')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('init', result.stderr)
        self.assertNotIn('Traceback', result.stderr)
        self.assertFalse(self.state.exists())

    def test_reinitialization_keeps_existing_bytes(self):
        self.assertSuccess(self.initialize())
        profile = self.state / 'subjects/synthetic/profile.json'
        profile.parent.mkdir(parents=True)
        profile.write_text('{"evidence": ["keep me"]}', encoding='utf-8')
        before = {p: p.read_bytes() for p in self.state.rglob('*.json')}
        self.assertNotEqual(self.initialize().returncode, 0)
        self.assertEqual(before, {p: p.read_bytes() for p in self.state.rglob('*.json')})

    def test_partial_configuration_is_not_replaced(self):
        self.state.mkdir()
        original = b'{"subjects": []}'
        (self.state / 'subjects.json').write_bytes(original)
        self.assertNotEqual(self.initialize().returncode, 0)
        self.assertEqual((self.state / 'subjects.json').read_bytes(), original)
        self.assertFalse((self.state / 'semester.json').exists())

    def test_invalid_input_does_not_create_config(self):
        for extra in [('--total-weeks', '0'), ('--timezone', 'Invalid/Zone'),
                      ('--week1-start', '2024-02-30'), ('--term-end', '2024-01-01'),
                      ('--vault-root', 'relative/path')]:
            with self.subTest(extra=extra):
                result = self.initialize(*extra)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((self.state / 'semester.json').exists())

    def test_existing_vault_and_empty_profile(self):
        self.assertSuccess(self.initialize())
        vault = self.base / 'existing-vault'
        course = vault / 'courses/math'
        course.mkdir(parents=True)
        note = course / 'notes.md'
        note.write_text('existing content', encoding='utf-8')
        result = self.assertSuccess(self.command('register', '--name', 'Synthetic math',
                                                 '--vault', vault, '--notes-root', course))
        profile = json.loads(Path(result['profile_path']).read_text(encoding='utf-8'))
        self.assertEqual(profile['topics'], [])
        self.assertEqual(note.read_text(), 'existing content')
        status = self.assertSuccess(self.command('status', '--subject', 'Synthetic math'))
        self.assertTrue(status['notes_root_exists'])

    def test_register_outside_vault_and_unsafe_name_fail(self):
        self.assertSuccess(self.initialize())
        vault = self.base / 'vault'
        outside = self.base / 'outside'
        vault.mkdir()
        outside.mkdir()
        result = self.command('register', '--name', 'Synthetic math', '--vault', vault,
                              '--notes-root', outside)
        self.assertNotEqual(result.returncode, 0)
        result = self.command('create-subject', '--name', '../escape')
        self.assertNotEqual(result.returncode, 0)
        registry = json.loads((self.state / 'subjects.json').read_text())
        self.assertEqual(registry['subjects'], [])

    def test_create_subject_preserves_existing_directory(self):
        self.assertSuccess(self.initialize())
        result = self.assertSuccess(self.command('create-subject', '--name', 'Synthetic course'))
        vault = Path(result['subject']['vault_path'])
        self.assertTrue((vault / '.obsidian').is_dir())
        marker = vault / 'keep.md'
        marker.write_text('keep', encoding='utf-8')
        result = self.assertSuccess(self.command('create-subject', '--name', 'Synthetic course'))
        self.assertEqual(result['result'], 'already_registered')
        self.assertEqual(marker.read_text(), 'keep')

    def test_concurrent_registration_retains_all_subjects(self):
        self.assertSuccess(self.initialize())
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')
        processes = []
        for i in range(6):
            args = [sys.executable, str(STATE_SCRIPT), '--state-dir', str(self.state),
                    'create-subject', '--name', f'Synthetic {i}']
            processes.append(subprocess.Popen(args, stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE, env=env))
        for process in processes:
            stdout, stderr = process.communicate(timeout=40)
            self.assertEqual(process.returncode, 0, stderr.decode('utf-8'))
        registry = json.loads((self.state / 'subjects.json').read_text())
        self.assertEqual(len(registry['subjects']), 6)
        for subject in registry['subjects']:
            self.assertTrue((self.state / 'subjects' / subject['id'] / 'profile.json').is_file())

    def test_installer_dry_run_writes_nothing(self):
        dest = self.base / 'install'
        result = run(INSTALL_SCRIPT, '--dest', dest, '--dry-run')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(dest.exists())

    def test_clean_install_then_initialize_installed_copy(self):
        dest = self.base / 'installed'
        result = run(INSTALL_SCRIPT, '--dest', dest)
        self.assertEqual(result.returncode, 0, result.stderr)
        for skill in ('semester-study-coach', 'obsidian-review-coach'):
            self.assertTrue((dest / skill / 'SKILL.md').is_file())
            self.assertFalse((dest / skill / 'state').exists())
        installed_script = dest / 'semester-study-coach/scripts/study_state.py'
        result = run(installed_script, 'init', '--week1-start', '2024-09-02',
                     '--total-weeks', '16', '--timezone', 'Asia/Shanghai',
                     '--vault-root', self.notes)
        self.assertSuccess(result)
        self.assertSuccess(run(installed_script, 'status'))

    def test_conflict_does_not_install_other_skill_or_modify_state(self):
        dest = self.base / 'installed'
        existing = dest / 'obsidian-review-coach/state'
        existing.mkdir(parents=True)
        marker = existing / 'private.json'
        marker.write_text('{"keep": true}', encoding='utf-8')
        result = run(INSTALL_SCRIPT, '--dest', dest)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((dest / 'semester-study-coach').exists())
        self.assertEqual(marker.read_text(), '{"keep": true}')


if __name__ == '__main__':
    unittest.main()
