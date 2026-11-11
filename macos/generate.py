#!/usr/bin/env python3
"""Private stdlib bridge. JSON stdin/stdout; never prints journal contents/errors."""
import datetime as dt
import json
import os
import pwd
import plistlib
from pathlib import Path
import subprocess
import sys
import tempfile

HOME = Path(pwd.getpwuid(os.getuid()).pw_dir)
ROOT = Path(os.environ.get('ASTRON_WIDGET_ROOT', HOME / 'Library/Application Support/astron'))
runtime_file = Path(__file__).with_name('runtime-paths.plist')
runtime = plistlib.loads(runtime_file.read_bytes()) if runtime_file.exists() else {}
SKILL = Path(os.environ.get('ASTRON_SKILL_ROOT', runtime.get('skill', str(Path(__file__).resolve().parent.parent))))
JOURNAL = Path(os.environ.get('ASTRON_JOURNAL_SCRIPT', SKILL / 'scripts/journal.py'))
PYTHON = Path(os.environ.get('ASTRON_PYTHON', runtime.get('python', str(HOME / '.local/share/astron/venv/bin/python'))))
SAFE = dict(topic='Ruang untuk refleksi', question='Apa yang ingin kamu beri perhatian hari ini?',
            action='Luangkan dua menit untuk mencatat satu pengalaman.', lesson_label='Belum ada pelajaran disetujui untuk dirujuk.')


def private_dir(path, create=False):
    if path.is_symlink():
        raise ValueError('Direktori privat tidak boleh berupa tautan.')
    if create:
        path.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not path.is_dir() or path.stat().st_mode & 0o077 or path.stat().st_uid != os.getuid():
        raise ValueError('Direktori jurnal harus milik pengguna dan bermode 0700.')
    return path


def settings():
    path = ROOT / 'widget-settings.json'
    if not path.exists():
        return {'journal_root': str(ROOT), 'profile_id': None}
    if path.is_symlink() or path.stat().st_mode & 0o077 or path.stat().st_uid != os.getuid():
        raise ValueError('Pengaturan widget harus privat (0600).')
    result = json.loads(path.read_text())
    if not isinstance(result, dict):
        raise ValueError('Pengaturan widget tidak valid.')
    return result


def write_private(name, value):
    private_dir(ROOT, create=True)
    target = ROOT / name
    if target.is_symlink():
        raise ValueError('Berkas privat tidak boleh berupa tautan.')
    fd, tmp = tempfile.mkstemp(prefix='.' + name, dir=ROOT)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, target)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def journal(cfg, payload):
    root = Path(cfg.get('journal_root') or ROOT).expanduser()
    if not root.is_absolute():
        raise ValueError('Lokasi jurnal harus absolut.')
    private_dir(root)
    # Read-only bridge requests never initialize a journal as a side effect.
    if not (root / 'journal.sqlite3').is_file():
        raise ValueError('Jurnal belum tersedia. Buat profil diri melalui Astron terlebih dahulu.')
    env = dict(os.environ, ASTRON_DATA_DIR=str(root))
    result = subprocess.run([sys.executable, str(JOURNAL)], input=json.dumps(payload),
                            text=True, capture_output=True, env=env, timeout=20)
    if result.returncode:
        raise ValueError('Operasi jurnal gagal. Tidak ada data pribadi ditampilkan.')
    return json.loads(result.stdout)


def require_self(cfg, ident):
    if not ident or not isinstance(ident, str):
        raise ValueError('Pilih profil diri sendiri terlebih dahulu.')
    profile = journal(cfg, {'operation': 'profile_get', 'profile_id': ident})
    if profile.get('relationship') != 'self' or profile.get('owner_consented') is not True:
        raise ValueError('Widget hanya mendukung profil diri yang disetujui.')


def refresh(cfg):
    value = dict(SAFE)
    selected = cfg.get('profile_id')
    if selected:
        require_self(cfg, selected)
        data = journal(cfg, {'operation': 'widget_data', 'profile_id': selected})
        # Only controlled generic text is cached. Never trust arbitrary free-text
        # fields from a journal (including an approved lesson) on the desktop.
        if data.get('question') == 'Apa yang paling terasa hari ini, sebelum membaca tafsir?':
            value['question'] = data['question']
        if data.get('action') in ('Coba satu langkah kecil yang sudah kamu pilih.', 'Pilih satu langkah kecil yang ada dalam kendalimu.'):
            value['action'] = data['action']
        approved = bool(data.get('lesson_id')) or data.get('has_approved_lesson') is True
        if approved:
            value['lesson_label'] = 'Ada pelajaran disetujui · tinjau secara privat di Astron.'
    value['date'] = dt.date.today().isoformat()
    write_private('widget-reflections.json', {'entries': [value]})
    return {'ok': True, 'selected': bool(selected), **value}


def execute(p):
    cfg = settings()
    op = p.get('operation', 'refresh')
    if op == 'sky':
        import sky_calendar
        month = p.get('month', dt.date.today().strftime('%Y-%m'))
        timezone = p.get('timezone', cfg.get('sky_timezone', 'Asia/Jakarta'))
        sky_calendar.bounds(month, timezone)
        personal = p.get('personal') is True
        natal = None
        if personal:
            if p.get('consent') is not True:
                raise ValueError('Explicit consent required for personal desktop interpretation.')
            ident = cfg.get('profile_id')
            require_self(cfg, ident)
            profile = journal(cfg, {'operation': 'profile_get', 'profile_id': ident})
            birth = profile.get('birth')
            if not isinstance(birth, dict) or not birth.get('time'):
                raise ValueError('A self profile with known birth time is required.')
            chart = sky_calendar.run_json(PYTHON, SKILL / 'scripts/chart.py', birth)
            natal = chart['points']
        data = sky_calendar.calculate(month, timezone, natal, PYTHON, SKILL)
        # No birth details, aliases, profile IDs or journal free text in cache.
        write_private('sky-calendar.json', data)
        return data
    if op == 'sky_clear':
        # Explicitly revoke personal display immediately, without calculator dependency.
        private_dir(ROOT, create=True)
        path = ROOT / 'sky-calendar.json'
        if path.is_symlink():
            raise ValueError('Refusing symlink cache.')
        if path.exists():
            path.unlink()
        return {'ok': True}
    if op == 'profiles':
        try:
            profiles = journal(cfg, {'operation': 'profiles'})
        except ValueError:
            return {'profiles': [], 'selected': cfg.get('profile_id'), 'journal_root': cfg.get('journal_root', str(ROOT)),
                    'notice': 'Jurnal belum tersedia atau tidak dapat dibaca. Widget generik tetap tersedia.'}
        return {'profiles': [{'id': x['id'], 'label': 'Profil diri ' + str(i + 1)} for i, x in enumerate(
                    x for x in profiles if x.get('relationship') == 'self' and x.get('owner_consented') is True)],
                'selected': cfg.get('profile_id'), 'journal_root': cfg.get('journal_root', str(ROOT))}
    if op == 'select':
        if p.get('consent') is not True:
            raise ValueError('Persetujuan eksplisit diperlukan untuk mengubah pilihan.')
        root = p.get('journal_root', cfg.get('journal_root', str(ROOT)))
        if not isinstance(root, str) or not Path(root).expanduser().is_absolute():
            raise ValueError('Lokasi jurnal harus absolut.')
        updated = {**cfg, 'journal_root': str(Path(root).expanduser()), 'profile_id': p.get('profile_id') or None}
        if updated['profile_id']:
            require_self(updated, updated['profile_id'])
        # Profile/root changes revoke any previously cached personal contacts.
        if updated.get('profile_id') != cfg.get('profile_id') or updated.get('journal_root') != cfg.get('journal_root'):
            cache = ROOT / 'sky-calendar.json'
            if cache.is_symlink():
                raise ValueError('Refusing symlink cache.')
            if cache.exists():
                cache.unlink()
        write_private('widget-settings.json', updated)
        # Immediately replace old cache even when no journal profile is selected.
        return refresh(updated)
    if op == 'learning':
        ident = cfg.get('profile_id')
        require_self(cfg, ident)
        result = journal(cfg, {'operation': 'learning', 'profile_id': ident})
        return {'lessons': [{'text': item['text']} for item in result.get('lessons', [])
                            if item.get('approved') is True and item.get('effective_status') in ('temporary', 'recurring')
                            and isinstance(item.get('text'), str)]}
    if op == 'capture':
        if p.get('consent') is not True:
            raise ValueError('Centang persetujuan penyimpanan terlebih dahulu.')
        experience = p.get('experience')
        if not isinstance(experience, str) or not experience.strip() or len(experience) > 10000:
            raise ValueError('Isi pengalaman 1–10000 karakter.')
        ident = cfg.get('profile_id')
        require_self(cfg, ident)
        today = dt.datetime.now(dt.timezone.utc).date().isoformat()
        result = journal(cfg, {'operation': 'checkin_add', 'profile_id': ident,
                               'experience': experience.strip(), 'consent': True,
                               'period_start': today, 'period_end': today,
                               'source': 'macOS companion: explicit owner capture', 'before_reveal': False})
        return {'ok': True, 'id': result['id']}
    if op == 'refresh':
        return refresh(cfg)
    raise ValueError('Operasi tidak dikenal.')


if __name__ == '__main__':
    os.umask(0o077)
    try:
        print(json.dumps(execute(json.load(sys.stdin)), ensure_ascii=False))
    except (ValueError, OSError, TypeError, KeyError, subprocess.SubprocessError):
        print(json.dumps({'error': 'Tidak dapat menyelesaikan operasi. Periksa profil diri, lokasi jurnal privat, dan persetujuan.'}))
        sys.exit(1)
