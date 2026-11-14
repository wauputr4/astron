import json
import math
import subprocess
import sys
import unittest
from pathlib import Path

from kerykeion.dignities import calculate_essential_dignity

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from chart import CLASSICAL_PLANETS, chaldean_face

BIRTH = {"date": "1990-07-15", "time": "10:30", "timezone": "Europe/Rome",
         "latitude": 41.9028, "longitude": 12.4964}


def calculate(script, payload):
    output = subprocess.check_output([sys.executable, str(SCRIPTS / script)],
                                    input=json.dumps(payload), text=True, stderr=subprocess.PIPE)
    return json.loads(output)


class DecanTest(unittest.TestCase):
    def test_all_intervals_match_kerykeion(self):
        signs = "Ari Tau Gem Can Leo Vir Lib Sco Sag Cap Aqu Pis".split()
        elements = ["Fire", "Earth", "Air", "Water"]
        for sector in range(36):
            start = sector * 10
            sign = sector // 3
            for lon in (start, start + 5, math.nextafter(start + 10, -math.inf)):
                with self.subTest(longitude=lon):
                    native = calculate_essential_dignity("Sun", signs[sign], elements[sign % 4],
                                                         lon - sign * 30, True)
                    self.assertEqual(chaldean_face(lon),
                                     {k: native[k] for k in ("decan_number", "decan_ruler")})
        self.assertEqual(chaldean_face(360), {"decan_number": 1, "decan_ruler": "Mars"})

    def test_both_natal_entry_points(self):
        simple = calculate("chart.py", {**BIRTH, "include_decans": True})
        full = calculate("astron.py", {"operation":"natal", "birth":BIRTH, "include_decans":True})
        self.assertEqual(simple["decan_system"], full["decan_system"])
        for planet in CLASSICAL_PLANETS:
            for field in ("decan_number", "decan_ruler"):
                self.assertEqual(simple["points"][planet][field], full["subject"][planet][field])
        self.assertEqual(full["subject"]["sun"]["decan_ruler"], "Moon")
        self.assertNotIn("decan_number", full["subject"]["uranus"])
        self.assertNotIn("decan_number", simple["points"]["uranus"])
        for script, payload, key in [("chart.py", BIRTH, "points"),
                                     ("astron.py", {"operation":"natal","birth":BIRTH}, "subject")]:
            plain = calculate(script, payload)
            self.assertNotIn("decan_ruler", plain[key]["sun"])
            self.assertNotIn("decan_system", plain)

    def test_unknown_time_is_a_noon_snapshot(self):
        noon = calculate("chart.py", {**BIRTH, "time":None, "include_decans":True})
        self.assertIsNone(noon["houses"])
        self.assertIn("noon", noon["warning"])
        self.assertIn("Decans", noon["warning"])
        self.assertIn("decan_number", noon["points"]["moon"])
