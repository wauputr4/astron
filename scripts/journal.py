"""Private, owner-scoped reflection journal. JSON stdin/stdout; stdlib only."""
import json
import os
from pathlib import Path
import sqlite3
import sys
from datetime import date, datetime, timezone
from uuid import uuid4

SCHEMA = """
CREATE TABLE IF NOT EXISTS profiles(id TEXT PRIMARY KEY, created_at TEXT NOT NULL, data TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS projections(id TEXT PRIMARY KEY, profile_id TEXT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE, created_at TEXT NOT NULL, data TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS reviews(id TEXT PRIMARY KEY, projection_id TEXT NOT NULL REFERENCES projections(id) ON DELETE CASCADE, created_at TEXT NOT NULL, data TEXT NOT NULL);
"""


def text(p, key):
    v = p.get(key)
    if not isinstance(v, str) or not v.strip():
        raise ValueError(f'{key} must be nonempty text')
    return v.strip()


def day(value):
    return date.fromisoformat(value).isoformat()


def execute(db, p):
    op = p.get('operation')
    now = datetime.now(timezone.utc).isoformat()
    def rows(table, where='', args=()):
        return [dict(id=r[0], created_at=r[1], **json.loads(r[2])) for r in db.execute(
            f'SELECT id, created_at, data FROM {table} {where} ORDER BY created_at, id', args)]
    def require(table, ident):
        r = rows(table, 'WHERE id=?', (ident,))
        if not r:
            raise ValueError(f'unknown {table} id')
        return r[0]
    def add(table, payload):
        ident = str(uuid4())
        db.execute(f'INSERT INTO {table} VALUES(?,?,?)', (ident, now, json.dumps(payload)))
        return dict(id=ident, created_at=now, **payload)
    if op == 'profile_add':
        if p.get('consent') is not True:
            raise ValueError('owner consent required to store profile')
        relation = text(p, 'relationship')
        if relation not in ('self', 'friend', 'colleague', 'acquaintance', 'partner', 'other'):
            raise ValueError('invalid relationship')
        # Birth information is optional; never infer it from observations.
        return add('profiles', dict(alias=text(p, 'alias'), relationship=relation,
            source=text(p, 'source'), notes=p.get('notes', ''), birth=p.get('birth'),
            owner_consented=True, subject_consent=p.get('subject_consent', 'unknown')))
    if op == 'profiles':
        return rows('profiles')
    if op == 'profile_get':
        return require('profiles', text(p, 'profile_id'))
    if op == 'profile_update':
        if p.get('consent') is not True:
            raise ValueError('consent required to update profile')
        ident = text(p, 'profile_id'); old = require('profiles', ident)
        changes = p.get('changes')
        allowed = {'alias', 'notes', 'birth', 'subject_consent'}
        if not isinstance(changes, dict) or not changes or not set(changes) <= allowed:
            raise ValueError('changes must contain supported profile fields')
        if 'alias' in changes:
            text(changes, 'alias')
        source = text(p, 'source')
        payload = {k: v for k, v in old.items() if k not in ('id', 'created_at')}
        payload['revisions'] = [*payload.get('revisions', []),
            dict(updated_at=now, source=source, previous={k: payload.get(k) for k in changes})]
        payload.update(changes)
        db.execute('UPDATE profiles SET data=? WHERE id=?', (json.dumps(payload), ident))
        return dict(id=ident, created_at=old['created_at'], **payload)
    if op == 'profile_delete':
        ident = text(p, 'profile_id'); require('profiles', ident)
        if p.get('confirm_delete') is not True:
            raise ValueError('explicit delete confirmation required')
        db.execute('DELETE FROM profiles WHERE id=?', (ident,))
        return {'deleted': ident, 'scope': 'profile and linked projections/reviews; backups not affected'}
    if op == 'projection_add':
        if p.get('consent') is not True:
            raise ValueError('consent required to store reflection')
        ident = text(p, 'profile_id'); require('profiles', ident)
        start, end = day(text(p, 'period_start')), day(text(p, 'period_end'))
        if end < start:
            raise ValueError('period_end precedes period_start')
        payload = dict(profile_id=ident, period_start=start, period_end=end,
            mode='prospective' if start > now[:10] else 'retrospective_or_ongoing',
            hypothesis=text(p, 'hypothesis'), basis=text(p, 'basis'),
            uncertainty=text(p, 'uncertainty'), would_not_fit=text(p, 'would_not_fit'),
            review_after=day(text(p, 'review_after')), context=p.get('context', ''),
            supersedes=p.get('supersedes'))
        if payload['review_after'] < end:
            raise ValueError('review_after must be on or after period_end')
        if payload['supersedes']:
            old = require('projections', payload['supersedes'])
            if old['profile_id'] != ident:
                raise ValueError('supersedes belongs to another profile')
        # Four columns: keep original hypothesis immutable; corrections are new records.
        uid = str(uuid4())
        db.execute('INSERT INTO projections VALUES(?,?,?,?)', (uid, ident, now, json.dumps(payload)))
        return dict(id=uid, created_at=now, **payload)
    if op == 'review_add':
        if p.get('consent') is not True:
            raise ValueError('consent required to store feedback')
        ident = text(p, 'projection_id'); require('projections', ident)
        outcome = text(p, 'outcome')
        if outcome not in ('matched', 'partial', 'missed', 'unclear', 'not_applicable'):
            raise ValueError('invalid outcome')
        payload = dict(projection_id=ident, outcome=outcome, experience=text(p, 'experience'),
            source=text(p, 'source'), lesson=p.get('lesson', ''),
            lesson_approved=p.get('lesson_approved') is True,
            supersedes=p.get('supersedes'))
        if payload['lesson_approved'] and not payload['lesson'].strip():
            raise ValueError('approved lesson must be nonempty')
        if payload['supersedes']:
            old = require('reviews', payload['supersedes'])
            if old['projection_id'] != ident:
                raise ValueError('supersedes belongs to another projection')
        existing = rows('reviews', 'WHERE projection_id=?', (ident,))
        replaced = {r['supersedes'] for r in existing if r.get('supersedes')}
        heads = [r for r in existing if r['id'] not in replaced]
        if heads and payload['supersedes'] != heads[-1]['id']:
            raise ValueError('review correction must supersede the latest review')
        uid = str(uuid4())
        db.execute('INSERT INTO reviews VALUES(?,?,?,?)', (uid, ident, now, json.dumps(payload)))
        return dict(id=uid, created_at=now, **payload)
    if op in ('history', 'due', 'learning'):
        ident = text(p, 'profile_id'); require('profiles', ident)
        projections = rows('projections', 'WHERE profile_id=?', (ident,))
        reviews = [r for item in projections for r in rows('reviews', 'WHERE projection_id=?', (item['id'],))]
        replaced = {r['supersedes'] for r in reviews if r.get('supersedes')}
        active = [r for r in reviews if r['id'] not in replaced]
        superseded = {r['supersedes'] for r in projections if r.get('supersedes')}
        if op == 'history':
            return dict(projections=projections, reviews=reviews)
        if op == 'due':
            today = now[:10]
            reviewed = {r['projection_id'] for r in active if r['outcome'] != 'unclear'}
            return [r for r in projections if r['review_after'] <= today and r['id'] not in reviewed and r['id'] not in superseded]
        counts = {key: sum(r['outcome'] == key for r in active) for key in ('matched', 'partial', 'missed', 'unclear', 'not_applicable')}
        return dict(outcomes=counts, reviewed_projections=len({r['projection_id'] for r in active}),
            lessons=[r for r in active if r['lesson_approved'] and r['lesson']],
            warning='Self-reported feedback, not predictive accuracy or scientific validation. Never apply lessons across profiles automatically.')
    raise ValueError('unknown operation')


def main():
    os.umask(0o077)
    p = json.load(sys.stdin)
    # Environment override is for isolated tests or an explicitly chosen private directory.
    default = Path.home() / ('Library/Application Support/astron' if sys.platform == 'darwin' else '.local/share/astron')
    root = Path(os.environ.get('ASTRON_DATA_DIR', default)).expanduser().resolve()
    repo = Path(__file__).resolve().parents[1]
    if root == repo or repo in root.parents:
        raise ValueError('journal must stay outside the skill repository')
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    if root.stat().st_mode & 0o077:
        raise ValueError('private data directory must have mode 0700')
    path = root / 'journal.sqlite3'
    if path.is_symlink():
        raise ValueError('refusing symlink database')
    if path.exists() and path.stat().st_mode & 0o077:
        raise ValueError('database must have mode 0600')
    with sqlite3.connect(path) as db:
        os.chmod(path, 0o600)
        db.execute('PRAGMA foreign_keys=ON')
        db.executescript(SCHEMA)
        result = execute(db, p)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, TypeError, sqlite3.Error, OSError) as exc:
        print(json.dumps({'error': str(exc)}), file=sys.stderr)
        sys.exit(1)
