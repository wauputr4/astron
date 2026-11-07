#!/usr/bin/env python3
"""Calculate a natal snapshot from JSON on stdin; emit JSON on stdout."""
import json
import sys
from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo

SIGNS = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces")

def main():
    import swisseph as swe
    data = json.load(sys.stdin)
    day = date.fromisoformat(data["date"])
    known = bool(data.get("time"))
    clock = time.fromisoformat(data["time"]) if known else time(12, 0)
    if clock.tzinfo is not None: raise ValueError("time must be local without an offset")
    lat, lon = float(data["latitude"]), float(data["longitude"])
    if not -90 <= lat <= 90 or not -180 <= lon <= 180: raise ValueError("invalid coordinates")
    tz = ZoneInfo(data["timezone"])
    naive = datetime.combine(day, clock)
    candidates = {naive.replace(tzinfo=tz, fold=f).astimezone(timezone.utc) for f in (0, 1)}
    valid = [x for x in candidates if x.astimezone(tz).replace(tzinfo=None) == naive]
    if len(valid) != 1: raise ValueError("ambiguous or nonexistent local time; clarify the UTC offset")
    utc = valid[0]
    hour = utc.hour + utc.minute / 60 + (utc.second + utc.microsecond / 1e6) / 3600
    jd = swe.julday(utc.year, utc.month, utc.day, hour)
    ids = {n: getattr(swe, n.upper()) for n in ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto")}
    ids.update({"true_node": swe.TRUE_NODE, "mean_lilith": swe.MEAN_APOG, "chiron": swe.CHIRON})
    def point(x):
        x = x % 360
        return {"longitude": round(x, 6), "sign": SIGNS[int(x // 30)], "degree_in_sign": round(x % 30, 6)}
    points, missing = {}, {}
    for name, ident in ids.items():
        try:
            values, flags = swe.calc_ut(jd, ident, swe.FLG_SWIEPH | swe.FLG_SPEED)
            points[name] = {**point(values[0]), "speed_degrees_per_day": round(values[3], 6), "retrograde": values[3] < 0, "returned_flags": flags}
        except swe.Error as exc:
            missing[name] = str(exc)
    aspects = []
    for i, (a, pa) in enumerate(points.items()):
        for b, pb in list(points.items())[i + 1:]:
            separation = abs(pa["longitude"] - pb["longitude"])
            separation = min(separation, 360 - separation)
            for name, angle in (("conjunction",0),("sextile",60),("square",90),("trine",120),("opposition",180)):
                orb = abs(separation-angle)
                if orb <= 6: aspects.append({"left":a,"right":b,"type":name,"orb":round(orb, 4)})
    houses = None
    warning = None
    if known:
        try:
            cusps, angles = swe.houses_ex(jd, lat, lon, b"P")
            houses = {"system":"Placidus", "ascendant":point(angles[0]), "midheaven":point(angles[1]), "cusps":[point(c) for c in cusps]}
            for obj in points.values():
                x = obj["longitude"]
                obj["house"] = next((i+1 for i, c in enumerate(cusps) if (x-c)%360 < (cusps[(i+1)%12]-c)%360), None)
        except swe.Error as exc: warning = "House calculation unavailable: " + str(exc)
    else:
        warning = "Unknown birth time: local noon assumed; positions and aspects can change, houses and angles omitted."
    result = {"method":{"zodiac":"tropical", "perspective":"geocentric apparent", "aspect_orb_degrees":6, "birth_time_known":known, "effective_local":naive.isoformat(), "timezone":data["timezone"], "utc":utc.isoformat(), "julian_day_ut":jd}, "points":points, "houses":houses, "aspects":aspects, "unavailable_points":missing, "warning":warning}
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2, allow_nan=False)
    print()

if __name__ == "__main__":
    try: main()
    except Exception as exc:
        print(f"Chart calculation failed: {exc}", file=sys.stderr)
        sys.exit(1)
