#!/usr/bin/env python3
"""Offline sky-event calendar; UTC bounds, local rendering. JSON on stdin/stdout."""
import json
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

def main():
    from kerykeion import LunationFinderFactory, MundaneAspectFactory, RetrogradeStationFactory
    import kerykeion
    from importlib.metadata import version
    x = json.load(sys.stdin)
    start, end = x["start_utc"], x["end_utc"]
    tz = ZoneInfo(x["timezone"])
    def event(kind, obj):
        data = obj.model_dump(mode="json", exclude_none=True)
        dt = datetime.fromisoformat(data["iso_utc"].replace("Z", "+00:00"))
        data["local_time"] = dt.astimezone(tz).isoformat()
        data["kind"] = kind
        return data
    moons = LunationFinderFactory.from_iso_range(start, end).lunations
    aspects = MundaneAspectFactory.from_iso_range(start, end, points=x.get("points"), aspects=x.get("aspects")).aspects
    stations = RetrogradeStationFactory.from_iso_range(start, end, planets=x.get("planets")).stations
    events = [event("lunation", z) for z in moons] + [event("aspect", z) for z in aspects] + [event("station", z) for z in stations]
    events.sort(key=lambda z: z["iso_utc"])
    json.dump({"method":{"library":"kerykeion", "version":version("kerykeion"), "backend":"libephemeris default unless environment overrides", "zodiac":"tropical", "range_utc":[start,end], "display_timezone":x["timezone"], "note":"Date-only end includes the full UTC day; not a personal transit calculator."}, "events":events},sys.stdout,ensure_ascii=False,allow_nan=False)
    print()
if __name__ == "__main__":
    try: main()
    except Exception as exc:
        print(f"Sky event calculation failed: {exc}",file=sys.stderr)
        sys.exit(1)
