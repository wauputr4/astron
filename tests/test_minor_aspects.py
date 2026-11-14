import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
ROME = {"date": "1990-07-15", "time": "10:30", "timezone": "Europe/Rome",
        "latitude": 41.9028, "longitude": 12.4964}


def natal(**options):
    raw = subprocess.check_output([sys.executable, str(SCRIPTS / "astron.py")],
                                  input=json.dumps({"operation": "natal", "birth": ROME, **options}),
                                  text=True, stderr=subprocess.PIPE)
    return json.loads(raw)["aspects"]


class MinorAspectTest(unittest.TestCase):
    def test_inconjunct_alias_preserves_major_aspects(self):
        default = natal()
        expanded = natal(minor_aspects=["quincunx", "inconjunct"])
        self.assertEqual(default, [a for a in expanded if a["aspect"] != "quincunx"])
        hits = [a for a in expanded if a["aspect"] == "quincunx"]
        self.assertTrue(all(abs(a["orbit"]) <= 2 for a in hits))
        pair = [a for a in hits if {a["p1_name"], a["p2_name"]} == {"Mercury", "Uranus"}]
        self.assertEqual(len(pair), 1)
        self.assertAlmostEqual(abs(pair[0]["orbit"]), 0.4734, places=3)
