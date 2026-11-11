import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import journal
import reflection
import unittest

class ReflectionTest(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:')
        self.addCleanup(self.db.close)
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript(journal.SCHEMA+reflection.SCHEMA)
        self.pid=self.call('profile_add',alias='SECRET NAME',relationship='self',source='owner')['id']
        self.other=self.call('profile_add',alias='Other',relationship='friend',source='owner')['id']
    def call(self,op,**kwargs):
        return journal.execute(self.db,dict(operation=op,consent=True,**kwargs))
    def projection(self,pid=None):
        return self.call('projection_add',profile_id=pid or self.pid,period_start='2020-01-01',period_end='2020-01-02',review_after='2020-01-03',hypothesis='SECRET HYPOTHESIS',basis='Synthetic fixture only',uncertainty='Symbolic',would_not_fit='Counterexample')['id']
    def review(self,projection_id=None,**kwargs):
        return self.call('review_add',projection_id=projection_id or self.projection(),outcome='partial',experience='Synthetic feedback',source='owner',**kwargs)
    def lesson(self,**kwargs):
        args=dict(profile_id=self.pid,review_id=self.review()['id'],text='PRIVATE LESSON',context='Work only',review_after='2099-01-01',approved=True,source='owner approved')
        return self.call('lesson_add',**{**args,**kwargs})
    def test_blind_due_does_not_reveal_hypothesis(self):
        ident=self.projection()
        data=self.call('blind_due',profile_id=self.pid)
        self.assertEqual(data[0]['id'],ident)
        self.assertNotIn('SECRET',json.dumps(data))
        self.assertEqual(set(data[0]),{'id','period_start','period_end','prompt'})
    def test_checkin_precedes_review_and_links_exact_period(self):
        ident=self.projection()
        checkin=self.call('checkin_add',profile_id=self.pid,period_start='2020-01-01',period_end='2020-01-02',experience='Before reading',source='owner',before_reveal=True)
        self.assertEqual(checkin['exposure'],'before_reveal')
        review=self.review(ident,checkin_id=checkin['id'],ratings={'fit':2,'usefulness':5,'clarity':3})
        self.assertEqual(review['ratings']['fit'],2)
        summary=self.call('learning',profile_id=self.pid)['rating_summary']
        self.assertEqual(summary['usefulness'],{'count':1,'mean':5.0})
        self.assertEqual(self.call('blind_due',profile_id=self.pid),[])
    def test_dimension_validation_and_no_default_rating(self):
        for ratings in [{'fit':True},{'usefulness':0},{'clarity':6},{'accuracy':3},{'fit':'5'}]:
            with self.assertRaises(ValueError): self.review(ratings=ratings)
        data=self.call('learning',profile_id=self.pid)['rating_summary']
        self.assertIsNone(data['fit']['mean'])
    def test_checkin_cross_subject_and_period_refused(self):
        for pid,start in [(self.other,'2020-01-01'),(self.pid,'2020-01-02')]:
            c=self.call('checkin_add',profile_id=pid,period_start=start,period_end='2020-01-02',experience='test',source='owner')
            with self.assertRaises(ValueError): self.review(checkin_id=c['id'])
    def test_lessons_expire_and_reapproval_has_revision(self):
        item=self.lesson(review_after='2020-01-03')
        self.assertEqual(self.call('lessons',profile_id=self.pid)[0]['effective_status'],'needs_review')
        self.assertEqual(self.call('learning',profile_id=self.pid)['lessons'],[])
        renewed=self.call('lesson_update',lesson_id=item['id'],source='owner renewal',changes={'review_after':'2099-01-01','status':'recurring'})
        self.assertEqual(renewed['effective_status'],'recurring')
        self.assertEqual(renewed['revisions'][0]['previous']['review_after'],'2020-01-03')
        self.assertEqual(len(self.call('learning',profile_id=self.pid)['lessons']),1)
        changed=self.call('lesson_update',lesson_id=item['id'],source='edit',changes={'text':'changed'})
        self.assertFalse(changed['approved'])
    def test_corrected_evidence_retires_usable_lesson(self):
        review=self.review();self.lesson(review_id=review['id'])
        self.review(review['projection_id'],supersedes=review['id'])
        self.assertEqual(self.call('learning',profile_id=self.pid)['lessons'],[])
        self.assertEqual(self.call('lessons',profile_id=self.pid)[0]['effective_status'],'needs_review')
    def test_lesson_profile_isolation_and_approval(self):
        self.lesson(approved=False)
        self.assertEqual(self.call('learning',profile_id=self.pid)['lessons'],[])
        with self.assertRaises(ValueError): self.lesson(profile_id=self.other)
        self.assertEqual(self.call('lessons',profile_id=self.other),[])
    def test_experiment_roundtrip(self):
        today=datetime.now(timezone.utc).date().isoformat()
        e=self.call('experiment_add',profile_id=self.pid,action='Ask one clear question',observation='Did clarification help?',context='work',period_start=today,period_end=today,source='owner')
        self.assertEqual(self.call('widget_data',profile_id=self.pid)['experiment_id'],e['id'])
        r=self.call('experiment_review',experiment_id=e['id'],performed='no',result='No opportunity',next_step='Try another time',source='owner')
        self.assertEqual(r['performed'],'no')
        self.assertIsNone(self.call('widget_data',profile_id=self.pid)['experiment_id'])
    def test_relationship_alternatives_need_counterevidence(self):
        alternative=dict(hypothesis='Busy',would_support='Says workload increased',would_weaken='Says workload is light',clarifying_question='Is now a good time?')
        with self.assertRaises(ValueError): self.call('relation_add',profile_id=self.other,alternatives=[alternative],observation='Slow response',source='owner',context='work')
        note=self.call('relation_add',profile_id=self.other,alternatives=[alternative,{**alternative,'hypothesis':'Different communication style'}],observation='Slow response',source='owner',context='work',helpful_communication='Agree response expectations')
        self.assertEqual(len(note['alternatives']),2)
        self.assertEqual(self.call('relations',profile_id=self.pid),[])
    def test_widget_is_privacy_safe_and_self_only(self):
        item=self.lesson()
        w=self.call('widget_data',profile_id=self.pid)
        self.assertEqual(w['lesson_id'],item['id'])
        self.assertNotIn('PRIVATE',json.dumps(w));self.assertNotIn('SECRET',json.dumps(w))
        with self.assertRaises(ValueError):self.call('widget_data',profile_id=self.other)
    def test_profile_delete_cascades_new_tables(self):
        self.lesson();self.call('checkin_add',profile_id=self.pid,period_start='2020-01-01',period_end='2020-01-02',experience='test',source='owner')
        self.call('profile_delete',profile_id=self.pid,confirm_delete=True)
        for table in ('lessons','checkins','experiments','relation_notes'):
            self.assertEqual(self.db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0],0)
    def test_legacy_schema_is_additive(self):
        # New tables are idempotent; old projections survive migration.
        ident=self.projection();self.db.executescript(journal.SCHEMA+reflection.SCHEMA)
        self.assertEqual(self.call('history',profile_id=self.pid)['projections'][0]['id'],ident)

if __name__=='__main__':unittest.main()
