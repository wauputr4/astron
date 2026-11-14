#!/usr/bin/env python3
"""Monthly sky calendar + event-time natal snapshots; JSON, local calculation only."""
import calendar
import datetime as dt
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from zoneinfo import ZoneInfo

UTC = dt.timezone.utc
PHASES = {'new': 'Bulan baru', 'full': 'Bulan purnama', 'first_quarter': 'Perbani awal', 'last_quarter': 'Perbani akhir'}
ASPECTS = {'conjunction': 'konjungsi', 'sextile': 'sekstil', 'square': 'kuadrat', 'trine': 'trigon', 'opposition': 'oposisi'}
PROMPTS = {
    'new': ('Ruang memulai', 'Pilih satu niat kecil; tidak perlu memulai semuanya sekaligus.'),
    'full': ('Ruang meninjau', 'Apa yang sudah terlihat jelas, dan apa yang belum kamu ketahui?'),
    'first_quarter': ('Ruang mencoba', 'Uji satu langkah kecil, lalu amati hasilnya.'),
    'last_quarter': ('Ruang merapikan', 'Tinjau satu kebiasaan yang masih berguna atau perlu diubah.'),
    'station': ('Ruang mengecek ulang', 'Periksa asumsi dan rencana; perubahan arah planet bukan jaminan gangguan.'),
    'aspect': ('Ruang menyelaraskan', 'Amati dua kebutuhan yang berbeda tanpa memaksakan satu kesimpulan.'),
}
BODIES = ('sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto')


def bounds(month, timezone):
    if not isinstance(month, str) or len(month) != 7:
        raise ValueError('month must be YYYY-MM')
    first = dt.date.fromisoformat(month + '-01')
    if not 1900 <= first.year <= 2100:
        raise ValueError('Supported calendar years: 1900–2100')
    zone = ZoneInfo(timezone)
    following = (first.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    start = dt.datetime.combine(first, dt.time(), zone)
    end = dt.datetime.combine(following, dt.time(), zone)
    return start, end


def contacts(moving, natal, orb=2.0):
    """Snapshot geometry only, NOT an exact personal-transit root or time window."""
    result = []
    for body, longitude in moving.items():
        for name, point in natal.items():
            if name not in BODIES:
                continue
            birth_lon = float(point['longitude'])
            if not math.isfinite(birth_lon) or not math.isfinite(float(longitude)):
                raise ValueError('Nonfinite longitude')
            separation = abs((float(longitude) - birth_lon + 180) % 360 - 180)
            for kind, angle in [('conjunction', 0), ('sextile', 60), ('square', 90), ('trine', 120), ('opposition', 180)]:
                distance = abs(separation - angle)
                if distance <= orb:
                    result.append({'moving': body, 'natal': name, 'aspect': kind, 'orb': round(distance, 4)})
    return sorted(result, key=lambda x: x['orb'])[:3]


def normalize(raw, natal=None):
    kind = raw['kind']
    instant = dt.datetime.fromisoformat(raw['iso_utc'].replace('Z', '+00:00'))
    moving = {}
    if kind == 'lunation':
        phase = raw['phase']
        subtype = {'new_moon': 'new', 'full_moon': 'full'}.get(phase, phase)
        if subtype not in PHASES:
            raise ValueError(f'Unsupported lunar phase: {phase}')
        title = PHASES[subtype]
        moving = {'Sun': raw['sun']['abs_pos'], 'Moon': raw['moon']['abs_pos']}
    elif kind == 'station':
        subtype = 'station'
        direction = 'mulai retrograde' if raw['station_type'] == 'SR' else 'kembali direct'
        title = raw['planet'] + ' ' + direction
        moving = {raw['planet']: raw['ecliptic_longitude']}
    elif kind == 'aspect':
        subtype = 'aspect'
        title = raw['point_a'] + ' ' + ASPECTS[raw['aspect']] + ' ' + raw['point_b']
        moving = {raw['point_a']: raw['point_a_longitude'], raw['point_b']: raw['point_b_longitude']}
    else:
        raise ValueError('Unsupported event kind')
    theme, interpretation = PROMPTS[subtype]
    linked = contacts(moving, natal) if natal is not None else []
    if linked:
        best = linked[0]
        domain = {'sun': 'tujuan dan prioritas', 'moon': 'kebutuhan dan kebiasaan', 'mercury': 'komunikasi dan cara belajar', 'venus': 'nilai dan hubungan', 'mars': 'tindakan dan batas', 'jupiter': 'kesempatan belajar', 'saturn': 'tanggung jawab dan struktur'}.get(best['natal'], 'pola perubahan')
        interpretation += ' Secara simbolik, amati ' + domain + '; cocokkan dengan pengalamanmu, bukan asumsi.'
        personal = f"{best['moving']} {ASPECTS[best['aspect']]} {best['natal'].title()} natal · orb {best['orb']:.2f}°"
    else:
        personal = 'Tidak ada kontak ≤2° pada titik yang diperiksa.' if natal is not None else 'Kaitan personal nonaktif.'
    return {'id': kind + ':' + raw['iso_utc'] + ':' + title, 'kind': kind, 'utc': instant.isoformat(),
            'local_time': raw['local_time'], 'day': raw['local_time'][:10], 'title': title,
            'theme': theme, 'interpretation': interpretation, 'personal': personal, 'contacts': linked,
            'personal_method': 'event_time_snapshot_not_exact_transit' if natal is not None else 'disabled'}


def run_json(python, script, payload):
    proc = subprocess.run([str(python), str(script)], input=json.dumps(payload), capture_output=True, text=True, timeout=180)
    if proc.returncode:
        raise ValueError('Local calculator failed; no synthetic events substituted.')
    return json.loads(proc.stdout)


def calculate(month, timezone='Asia/Jakarta', natal=None, python=None, skill=None):
    start, end = bounds(month, timezone)
    skill = Path(skill or Path(__file__).resolve().parent.parent)
    python = python or sys.executable
    payload = {'start_utc': start.astimezone(UTC).isoformat(),
               'end_utc': (end.astimezone(UTC) - dt.timedelta(seconds=1)).isoformat(),
               'timezone': timezone, 'points': ['Sun', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn'],
               'aspects': ['conjunction', 'square', 'trine', 'opposition'], 'planets': ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']}
    raw = run_json(python, skill / 'scripts/sky_events.py', payload)
    events = [normalize(e, natal) for e in raw['events']
              if start <= dt.datetime.fromisoformat(e['local_time']) < end]
    return {'month': month, 'timezone': timezone, 'days': calendar.monthrange(start.year, start.month)[1],
            'first_weekday': start.weekday(), 'events': events, 'generated_utc': dt.datetime.now(UTC).isoformat(),
            'personal_enabled': natal is not None, 'method': raw['method'],
            'notice': 'Interpretasi simbolik, bukan kepastian kejadian. Kontak natal adalah snapshot waktu peristiwa; bukan waktu transit personal eksak.',
            'scope': 'Lunations; selected planetary aspects and stations. No eclipse/visibility forecast.'}


if __name__ == '__main__':
    try:
        p = json.load(sys.stdin)
        print(json.dumps(calculate(p['month'], p.get('timezone', 'Asia/Jakarta')), ensure_ascii=False, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError):
        print(json.dumps({'error': 'Sky calendar calculation failed; check month, timezone and local dependencies.'}))
        sys.exit(1)
