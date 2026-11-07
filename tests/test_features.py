import json, os, subprocess, sys, tempfile, unittest, xml.etree.ElementTree as ET
from pathlib import Path
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "astron.py"
BIRTH = {"date":"1990-07-15", "time":"10:30", "timezone":"Europe/Rome", "latitude":41.9028, "longitude":12.4964}
def run(operation, birth=BIRTH, **kwargs):
    return subprocess.run([sys.executable,str(SCRIPT)],input=json.dumps({"operation":operation,"birth":birth,**kwargs}),capture_output=True,text=True)
class AstronTest(unittest.TestCase):
    def test_natal_against_published_example(self):
        r=run("natal"); self.assertEqual(r.returncode,0,r.stderr)
        sun=json.loads(r.stdout)["subject"]["sun"]
        self.assertEqual(sun["sign"],"Can"); self.assertAlmostEqual(sun["position"],22.607,places=2)
    def test_svg_is_valid_private_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"chart.svg"; r=run("svg",output=str(f)); self.assertEqual(r.returncode,0,r.stderr)
            self.assertTrue(ET.parse(f).getroot().tag.endswith("svg")); self.assertEqual(f.stat().st_mode & 0o777,0o600)
            self.assertNotIn("Greenwich",f.read_text()); self.assertNotEqual(run("svg",output=str(f)).returncode,0)
    def test_json_export_is_private_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"natal.json"; r=run("natal",output=str(f)); self.assertEqual(r.returncode,0,r.stderr)
            self.assertEqual(json.loads(f.read_text())["subject"]["sun"]["sign"],"Can")
            self.assertEqual(f.stat().st_mode & 0o777,0o600)
            self.assertNotEqual(run("natal",output=str(f)).returncode,0)
    def test_transit_range_and_clipped_exact(self):
        r=run("transits",start_utc="2026-11-01T00:00:00Z",end_utc="2026-11-08T00:00:00Z"); self.assertEqual(r.returncode,0,r.stderr)
        events=json.loads(r.stdout)["data"]["events"]; self.assertTrue(events)
        for e in events:
            if e.get("min_orb",999)>0.01: self.assertNotIn("exact_moment",e)
        self.assertNotIn("sampling step",r.stderr)
    def test_progression(self):
        r=run("progression",target_utc="2026-07-15T00:00:00Z"); self.assertEqual(r.returncode,0,r.stderr)
        self.assertTrue(json.loads(r.stdout)["ephemeris_iso_utc_datetime"].startswith("1990-08-20"))
    def test_sky_lunations_against_usno(self):
        sky=SCRIPT.parent/"sky_events.py"
        payload={"start_utc":"2026-11-01","end_utc":"2026-11-30","timezone":"Asia/Jakarta","points":["Sun","Mercury"],"aspects":["conjunction"],"planets":["Mercury"]}
        r=subprocess.run([sys.executable,str(sky)],input=json.dumps(payload),text=True,capture_output=True)
        self.assertEqual(r.returncode,0,r.stderr)
        events=json.loads(r.stdout)["events"]
        self.assertTrue(any(e.get("phase")=="new" and e["iso_utc"].startswith("2026-11-09T07:02") for e in events))
        self.assertTrue(any(e.get("phase")=="full" and e["iso_utc"].startswith("2026-11-24T14:53") for e in events))
    def test_unknown_time_and_dst_refused(self):
        for b in [{**BIRTH,"time":None},{**BIRTH,"date":"2024-11-03","time":"01:30","timezone":"America/New_York"}]:
            self.assertNotEqual(run("natal",birth=b).returncode,0)
if __name__ == "__main__": unittest.main()
