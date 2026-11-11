import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/journal.py'

class JournalTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.env = {**os.environ, 'ASTRON_DATA_DIR': self.tmp.name}
    def call(self, operation, ok=True, **kwargs):
        r = subprocess.run([sys.executable, str(SCRIPT)], input=json.dumps(dict(operation=operation, **kwargs)), text=True, capture_output=True, env=self.env)
        self.assertEqual(r.returncode == 0, ok, r.stderr)
        return json.loads(r.stdout if ok else r.stderr)
    def profile(self, alias='Sample'):
        return self.call('profile_add', consent=True, alias=alias, relationship='friend', source='owner observations')['id']
    def projection(self, pid, **kwargs):
        p = dict(profile_id=pid, consent=True, period_start='2020-01-01', period_end='2020-01-02', review_after='2020-01-03', hypothesis='Communication may feel demanding', basis='Illustrative only, no calculated chart', uncertainty='Symbolic, not a prediction', would_not_fit='Communication feels easy')
        return self.call('projection_add', **{**p, **kwargs})
    def review(self, ident, **kwargs):
        p = dict(projection_id=ident, consent=True, outcome='missed', experience='It felt easy', source='owner retrospective account', lesson='Ask before assuming difficulty', lesson_approved=True)
        return self.call('review_add', **{**p, **kwargs})
    def test_roundtrip_private_and_isolated(self):
        pid = self.profile(); other = self.profile('Other')
        item = self.projection(pid)
        self.assertEqual(item['mode'], 'retrospective_or_ongoing')
        self.assertEqual(len(self.call('due', profile_id=pid)), 1)
        self.review(item['id'])
        self.assertEqual(self.call('due', profile_id=pid), [])
        learning = self.call('learning', profile_id=pid)
        self.assertEqual(learning['outcomes']['missed'], 1)
        self.assertEqual(len(learning['legacy_lessons']), 1)
        self.assertEqual(self.call('learning', profile_id=other)['lessons'], [])
        self.assertEqual((Path(self.tmp.name)/'journal.sqlite3').stat().st_mode & 0o777, 0o600)
    def test_corrections_preserve_original_and_do_not_double_count(self):
        pid = self.profile(); item = self.projection(pid)
        old = self.review(item['id'], outcome='unclear', lesson_approved=False)
        self.assertEqual(len(self.call('due', profile_id=pid)), 1)
        self.review(item['id'], supersedes=old['id'])
        history = self.call('history', profile_id=pid)
        self.assertEqual(len(history['reviews']), 2)
        self.assertEqual(history['projections'][0]['hypothesis'], item['hypothesis'])
        self.assertEqual(self.call('learning', profile_id=pid)['reviewed_projections'], 1)
        self.call('review_add', ok=False, projection_id=item['id'], consent=True, outcome='matched', experience='Changed', source='owner')
    def test_profile_update_preserves_previous_values(self):
        pid = self.profile()
        item = self.projection(pid)
        self.call('profile_update', ok=False, profile_id=pid, changes={'alias':'New'}, source='owner')
        changed = self.call('profile_update', profile_id=pid, consent=True, changes={'alias':'New'}, source='owner correction')
        self.assertEqual(changed['alias'], 'New')
        self.assertEqual(changed['revisions'][0]['previous']['alias'], 'Sample')
        self.assertEqual(self.call('history', profile_id=pid)['projections'][0]['id'], item['id'])

    def test_future_and_supersession(self):
        pid = self.profile()
        old = self.projection(pid)
        future = self.projection(pid, period_start='2099-01-01', period_end='2099-01-02', review_after='2099-01-03', supersedes=old['id'])
        self.assertEqual(future['mode'], 'prospective')
        self.assertEqual(self.call('due', profile_id=pid), [])
    def test_consent_unknown_ids_and_dates(self):
        self.call('profile_add', ok=False, alias='No consent', relationship='self', source='owner')
        pid = self.profile()
        self.call('projection_add', ok=False, profile_id=pid, consent=True, period_start='bad')
        self.call('profile_get', ok=False, profile_id='missing')
        self.call('review_add', ok=False, projection_id='missing', consent=True)
    def test_delete_cascades_and_requires_confirmation(self):
        pid = self.profile(); item = self.projection(pid); self.review(item['id'])
        self.call('profile_delete', ok=False, profile_id=pid)
        self.call('profile_delete', profile_id=pid, confirm_delete=True)
        self.assertEqual(self.call('profiles'), [])
        self.call('history', ok=False, profile_id=pid)
    def test_cross_profile_correction_refused(self):
        one, two = self.profile(), self.profile('Other')
        old = self.projection(one)
        p = dict(profile_id=two, consent=True, period_start='2020-01-01', period_end='2020-01-02', review_after='2020-01-03', hypothesis='test', basis='test', uncertainty='test', would_not_fit='test', supersedes=old['id'])
        self.call('projection_add', ok=False, **p)
    def test_insecure_directory_refused(self):
        os.chmod(self.tmp.name, 0o755)
        self.call('profiles', ok=False)
        os.chmod(self.tmp.name, 0o700)
    def test_cli_reports_malformed_json(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], input='{', text=True, capture_output=True, env=self.env)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('error', json.loads(r.stderr))

if __name__ == '__main__':
    unittest.main()
