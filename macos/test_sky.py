"""Synthetic privacy/geometry tests plus one actual offline monthly calculation."""
import datetime as dt
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import sky_calendar as sky
import generate

class CalendarTest(unittest.TestCase):
    def test_local_month_bounds_and_leap_year(self):
        start, end = sky.bounds('2024-02', 'Asia/Jakarta')
        self.assertEqual(start.astimezone(dt.timezone.utc).isoformat(), '2024-01-31T17:00:00+00:00')
        self.assertEqual((end-start).days, 29)
        with self.assertRaises(ValueError): sky.bounds('2026-13', 'UTC')
        with self.assertRaises(ValueError): sky.bounds('2026-1', 'UTC')

    def test_dst_month(self):
        start, end = sky.bounds('2026-03', 'America/New_York')
        self.assertNotEqual(start.utcoffset(), end.utcoffset())

    def test_geometry_wrap_orb_and_no_claim_of_exact(self):
        result = sky.contacts({'Sun': 359.5}, {'sun': {'longitude': 0.5}})
        self.assertEqual(result[0]['orb'], 1.0)
        self.assertEqual(result[0]['aspect'], 'conjunction')
        self.assertEqual(sky.contacts({'Sun': 357}, {'sun': {'longitude': 0}}), [])
        with self.assertRaises(ValueError): sky.contacts({'Sun': float('nan')}, {'sun': {'longitude': 0}})

    def test_normalization_personal_is_snapshot(self):
        event = {'kind': 'station', 'planet': 'Mercury', 'station_type': 'SD', 'ecliptic_longitude': 10,
                 'iso_utc': '2026-11-13T15:53:52Z', 'local_time': '2026-11-13T22:53:52+07:00'}
        general = sky.normalize(event)
        self.assertEqual(general['personal_method'], 'disabled')
        own = sky.normalize(event, {'moon': {'longitude': 10}})
        self.assertEqual(own['personal_method'], 'event_time_snapshot_not_exact_transit')
        self.assertIn('kebutuhan', own['interpretation'])
        self.assertEqual(own['day'], '2026-11-13')
        self.assertIn('direct', own['title'])

    def test_real_month_and_no_birth_data(self):
        result = sky.calculate('2026-11', 'Asia/Jakarta')
        self.assertEqual(result['days'], 30)
        self.assertGreaterEqual(len(result['events']), 4)
        self.assertTrue(all(e['day'].startswith('2026-11-') for e in result['events']))
        self.assertEqual(result['events'], sorted(result['events'], key=lambda e: e['utc']))
        self.assertTrue(any(e['kind'] == 'lunation' for e in result['events']))
        self.assertFalse(result['personal_enabled'])
        self.assertNotIn('birth', result)
        self.assertTrue(all(not e['contacts'] for e in result['events']))
        self.assertIn('kerykeion', result['method']['library'])

    def test_private_cache_consent_and_clear(self):
        with tempfile.TemporaryDirectory() as d, patch.object(generate, 'ROOT', Path(d)):
            os.chmod(d, 0o700)
            with self.assertRaises(ValueError):
                generate.execute({'operation': 'sky', 'personal': True, 'month': '2026-11'})
            with patch.object(sky, 'calculate', return_value={'events': [], 'personal_enabled': False}):
                result = generate.execute({'operation': 'sky', 'month': '2026-11'})
                self.assertFalse(result['personal_enabled'])
                self.assertEqual((Path(d)/'sky-calendar.json').stat().st_mode & 0o777, 0o600)
                generate.execute({'operation': 'sky_clear'})
                self.assertFalse((Path(d)/'sky-calendar.json').exists())
                self.assertFalse((Path(d)/'journal.sqlite3').exists())

    def test_personal_requires_self_and_known_time(self):
        with tempfile.TemporaryDirectory() as d, patch.object(generate, 'ROOT', Path(d)), \
             patch.object(generate, 'settings', return_value={'profile_id': 'synthetic'}), \
             patch.object(generate, 'require_self') as own, \
             patch.object(generate, 'journal', return_value={'birth': {'date': '1990-01-01'}}):
            os.chmod(d, 0o700)
            with self.assertRaises(ValueError):
                generate.execute({'operation': 'sky', 'month': '2026-11', 'personal': True, 'consent': True})
            own.assert_called_once()
            self.assertFalse((Path(d)/'sky-calendar.json').exists())

    def test_synthetic_personal_roundtrip_and_profile_revocation(self):
        with tempfile.TemporaryDirectory() as d, patch.object(generate, 'ROOT', Path(d)):
            os.chmod(d, 0o700)
            cfg = {'profile_id': 'synthetic', 'journal_root': d}
            profile = {'birth': {'date': '1990-07-15', 'time': '10:30', 'timezone': 'Europe/Rome',
                                  'latitude': 41.9028, 'longitude': 12.4964}}
            with patch.object(generate, 'settings', return_value=cfg), patch.object(generate, 'require_self'), \
                 patch.object(generate, 'journal', return_value=profile):
                data = generate.execute({'operation': 'sky', 'month': '2026-11', 'personal': True, 'consent': True})
                self.assertTrue(data['personal_enabled'])
                self.assertTrue(any(e['contacts'] for e in data['events']))
                raw = (Path(d)/'sky-calendar.json').read_text()
                self.assertNotIn('1990-07-15', raw)
                self.assertNotIn('synthetic', raw)
                generate.execute({'operation': 'select', 'profile_id': None, 'consent': True})
                self.assertFalse((Path(d)/'sky-calendar.json').exists())

    def test_clear_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as d, patch.object(generate, 'ROOT', Path(d)):
            os.chmod(d, 0o700)
            (Path(d)/'sky-calendar.json').symlink_to(Path(d)/'other')
            with self.assertRaises(ValueError): generate.execute({'operation': 'sky_clear'})

if __name__ == '__main__': unittest.main()
