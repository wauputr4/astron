#!/usr/bin/env python3
"""Local structured natal, transit, progression, and SVG calculations. JSON stdin."""
import json, sys, os
from datetime import datetime, date, time, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

def subject(x):
    from kerykeion import AstrologicalSubjectFactory
    day = date.fromisoformat(x["date"])
    if not x.get("time"): raise ValueError("Exact birth time required for this operation; use chart.py for unknown time")
    clock = time.fromisoformat(x["time"])
    if clock.tzinfo or clock.second or clock.microsecond: raise ValueError("Use local HH:MM")
    lat, lon = float(x["latitude"]), float(x["longitude"])
    if not -90 <= lat <= 90 or not -180 <= lon <= 180: raise ValueError("Invalid coordinates")
    zone = ZoneInfo(x["timezone"])
    naive = datetime.combine(day, clock)
    candidates = {naive.replace(tzinfo=zone, fold=f).astimezone(timezone.utc) for f in (0,1)}
    if len([a for a in candidates if a.astimezone(zone).replace(tzinfo=None)==naive]) != 1: raise ValueError("Ambiguous or nonexistent local time")
    return AstrologicalSubjectFactory.from_birth_data(name="Natal",city="Birthplace",nation="",year=day.year,month=day.month,day=day.day,hour=clock.hour,minute=clock.minute,lat=lat,lng=lon,tz_str=x["timezone"],online=False)

def main():
    from kerykeion import ChartDataFactory, ChartDrawer, EphemerisDataFactory, TransitsTimeRangeFactory, SecondaryProgressionFactory
    x=json.load(sys.stdin); op=x["operation"]; s=subject(x["birth"])
    if op == "natal":
        result=ChartDataFactory.create_natal_chart_data(s).model_dump(mode="json",exclude_none=True)
    elif op == "svg":
        out=Path(x["output"]).expanduser().resolve()
        if out.suffix.lower() != ".svg": raise ValueError("Output must have .svg suffix")
        if out.exists(): raise ValueError("Output already exists")
        out.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
        svg = ChartDrawer(ChartDataFactory.create_natal_chart_data(s)).generate_svg_string(remove_css_variables=True)
        fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f: f.write(svg)
        result={"output":str(out),"format":"svg","private":True}
    elif op == "transits":
        start=datetime.fromisoformat(x["start_utc"].replace("Z","+00:00")); end=datetime.fromisoformat(x["end_utc"].replace("Z","+00:00"))
        if start.utcoffset() is None or end.utcoffset() is None or start>=end: raise ValueError("Provide increasing timezone-aware UTC bounds")
        if (end-start).days>370: raise ValueError("Maximum range is 370 days")
        start=start.astimezone(timezone.utc); end=end.astimezone(timezone.utc)
        pts=["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"]
        eph=EphemerisDataFactory(start,end,step_type="hours",step=2,lat=float(x["birth"]["latitude"]),lng=float(x["birth"]["longitude"]),tz_str="Etc/UTC",active_points=pts)
        samples=eph.get_ephemeris_data_as_astrological_subjects()
        result=TransitsTimeRangeFactory(s,samples,active_points=pts).get_transit_events(refine_exact_moments=True).model_dump(mode="json",exclude_none=True)
        for ev in result.get("events", []):
            if ev.get("min_orb", 999) > 0.01 and ev.get("exact_moment"):
                ev["closest_sample_moment"] = ev.pop("exact_moment")
                ev["exact_not_verified"] = True
        result={"method":{"sampling_hours":2,"refine_exact_moments":True,"range_start":start.isoformat(),"range_end":end.isoformat(),"note":"Orb windows and exact times depend on sampling and library defaults; range edges may be clipped."},"data":result}
    elif op == "progression":
        result=SecondaryProgressionFactory.compute_full(s,target_iso_utc_datetime=x["target_utc"]).model_dump(mode="json",exclude_none=True)
    else: raise ValueError("operation must be natal, svg, transits, or progression")
    if op != "svg" and x.get("output"):
        out = Path(x["output"]).expanduser().resolve()
        if out.suffix.lower() != ".json": raise ValueError("JSON output must have .json suffix")
        out.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
        fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f: json.dump(result,f,ensure_ascii=False,allow_nan=False,indent=2)
        result = {"output":str(out),"format":"json","private":True}
    json.dump(result,sys.stdout,ensure_ascii=False,allow_nan=False); print()
if __name__=="__main__":
    try: main()
    except Exception as e:
        print(f"Astron calculation failed: {e}",file=sys.stderr); sys.exit(1)
