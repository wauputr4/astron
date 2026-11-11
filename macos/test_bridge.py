"""Synthetic isolated tests; no reads of the owner's real profiles."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
JOURNAL = HERE.parent / 'scripts/journal.py'


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        os.chmod(self.root, 0o700)
        self.env = dict(os.environ, ASTRON_WIDGET_ROOT=str(self.root), ASTRON_DATA_DIR=str(self.root), ASTRON_JOURNAL_SCRIPT=str(JOURNAL))

    def tearDown(self):
        self.temp.cleanup()

    def call(self, script, payload, ok=True):
        result = subprocess.run(['/usr/bin/python3', str(script)], input=json.dumps(payload), capture_output=True, text=True, env=self.env)
        self.assertEqual(result.returncode == 0, ok, result.stdout + result.stderr)
        return json.loads(result.stdout) if result.stdout else None

    def journal(self, operation, **kw):
        return self.call(JOURNAL, dict(operation=operation, **kw))

    def bridge(self, operation, ok=True, **kw):
        return self.call(HERE / 'generate.py', dict(operation=operation, **kw), ok)

    def profile(self, relationship='self'):
        return self.journal('profile_add', alias='PRIVATE NAME NEVER ON WIDGET', relationship=relationship, source='Synthetic test', notes='PRIVATE RELATION DETAILS', consent=True)['id']

    def test_generic_without_journal(self):
        result = self.bridge('refresh')
        self.assertFalse(result['selected'])
        self.assertFalse((self.root / 'journal.sqlite3').exists())
        self.assertEqual((self.root / 'widget-reflections.json').stat().st_mode & 0o777, 0o600)
        self.assertFalse((self.root / 'widget-settings.json').exists())

    def test_self_only_and_explicit_selection(self):
        own = self.profile()
        friend = self.profile('friend')
        profiles = self.bridge('profiles')['profiles']
        self.assertEqual([x['id'] for x in profiles], [own])
        self.assertNotIn('PRIVATE', json.dumps(profiles))
        self.bridge('select', profile_id=friend, consent=True, ok=False)
        self.bridge('select', profile_id=own, consent=False, ok=False)
        self.assertFalse((self.root / 'widget-settings.json').exists())
        self.bridge('capture', experience='should not save', consent=True, ok=False)

    def test_capture_and_privacy(self):
        own = self.profile()
        selected = self.bridge('select', profile_id=own, consent=True)
        self.assertTrue(selected['selected'])
        self.bridge('capture', experience='PRIVATE EXPERIENCE', consent=False, ok=False)
        note = self.bridge('capture', experience='PRIVATE EXPERIENCE', consent=True)
        self.assertTrue(note['id'])
        saved = self.journal('checkins', profile_id=own)
        self.assertEqual(saved[-1]['experience'], 'PRIVATE EXPERIENCE')
        self.assertEqual(saved[-1]['exposure'], 'unknown_or_exposed')
        cache = (self.root / 'widget-reflections.json').read_text()
        self.assertNotIn('PRIVATE', cache)
        self.assertNotIn(own, cache)
        self.assertEqual((self.root / 'widget-settings.json').stat().st_mode & 0o777, 0o600)
        self.bridge('select', profile_id='', consent=True)
        self.assertFalse(self.bridge('refresh')['selected'])

    def test_settings_merge_and_symlink_rejection(self):
        target = self.root / 'widget-settings.json'
        target.write_text(json.dumps({'journal_root': str(self.root), 'profile_id': None, 'future_option': 42}))
        target.chmod(0o600)
        self.bridge('select', profile_id='', consent=True)
        self.assertEqual(json.loads(target.read_text())['future_option'], 42)
        target.unlink()
        target.symlink_to(self.root / 'missing')
        self.bridge('select', profile_id='', consent=True, ok=False)

    def test_private_directory_required(self):
        own = self.profile()
        self.root.chmod(0o755)
        self.bridge('select', profile_id=own, consent=True, ok=False)

    def test_approved_lesson_reference_not_text(self):
        own = self.profile()
        projection = self.journal('projection_add', profile_id=own, consent=True, period_start='2026-01-01', period_end='2026-01-02', hypothesis='Synthetic', basis='Synthetic', uncertainty='Uncertain', would_not_fit='Counterexample', review_after='2026-01-02')
        review = self.journal('review_add', projection_id=projection['id'], consent=True, outcome='missed', experience='PRIVATE EXPERIENCE', source='Synthetic', lesson='PRIVATE LEGACY LESSON', lesson_approved=True)
        self.journal('lesson_add', profile_id=own, review_id=review['id'], consent=True, text='PRIVATE LESSON', context='Synthetic only', source='Synthetic owner', approved=True, status='recurring', review_after='2099-01-01')
        self.bridge('select', profile_id=own, consent=True)
        self.assertEqual(self.bridge('learning')['lessons'], [{'text': 'PRIVATE LESSON'}])
        cache = (self.root / 'widget-reflections.json').read_text()
        self.assertIn('Ada pelajaran disetujui', cache)
        self.assertNotIn('PRIVATE', cache)

    def test_widget_rejects_arbitrary_journal_text(self):
        self.profile()
        fake = self.root / 'fake_journal.py'
        fake.write_text("import json,sys\np=json.load(sys.stdin)\nprint(json.dumps({'relationship':'self','owner_consented':True} if p['operation']=='profile_get' else {'question':'PRIVATE QUESTION','action':'PRIVATE ACTION','lesson':'PRIVATE LESSON','lesson_id':'synthetic'}))\n")
        self.env['ASTRON_JOURNAL_SCRIPT'] = str(fake)
        self.bridge('select', profile_id='synthetic', consent=True)
        cache = (self.root / 'widget-reflections.json').read_text()
        self.assertNotIn('PRIVATE', cache)
        self.assertNotIn('synthetic', cache)
        self.assertIn('Ada pelajaran disetujui', cache)


if __name__ == '__main__':
    unittest.main()
