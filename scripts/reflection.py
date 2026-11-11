"""Reflective workflows on the existing private SQLite journal (stdlib only)."""
import json
from datetime import date, datetime, timezone
from uuid import uuid4

SCHEMA = '''
CREATE TABLE IF NOT EXISTS checkins(id TEXT PRIMARY KEY, profile_id TEXT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE, created_at TEXT NOT NULL, data TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS lessons(id TEXT PRIMARY KEY, profile_id TEXT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE, created_at TEXT NOT NULL, data TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS experiments(id TEXT PRIMARY KEY, profile_id TEXT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE, created_at TEXT NOT NULL, data TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS relation_notes(id TEXT PRIMARY KEY, profile_id TEXT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE, created_at TEXT NOT NULL, data TEXT NOT NULL);
'''
OPS = {'checkin_add', 'checkins', 'blind_due', 'lesson_add', 'lesson_update', 'lessons',
       'experiment_add', 'experiment_review', 'experiments', 'relation_add', 'relations',
       'widget_data'}


def execute(db, p):
    # Imported lazily to keep journal.py the single validation/storage entry point.
    from journal import text, day
    op = p['operation']
    now = datetime.now(timezone.utc).isoformat()
    today = now[:10]
    def rows(table, key, ident):
        return [dict(id=r[0], created_at=r[1], **json.loads(r[2])) for r in db.execute(
            f'SELECT id,created_at,data FROM {table} WHERE {key}=? ORDER BY created_at,id', (ident,))]
    def require(table, ident):
        items = rows(table, 'id', ident)
        if not items:
            raise ValueError(f'unknown {table} id')
        return items[0]
    def consent():
        if p.get('consent') is not True:
            raise ValueError('explicit storage consent required')
    def add(table, profile_id, data):
        uid = str(uuid4())
        db.execute(f'INSERT INTO {table} VALUES(?,?,?,?)', (uid, profile_id, now, json.dumps(data)))
        return dict(id=uid, created_at=now, **data)
    def update(table, old, changes):
        data = {k:v for k,v in old.items() if k not in ('id','created_at')}
        data['revisions'] = [*data.get('revisions', []), dict(updated_at=now, previous={k:data.get(k) for k in changes}, source=text(p,'source'))]
        data.update(changes)
        db.execute(f'UPDATE {table} SET data=? WHERE id=?', (json.dumps(data),old['id']))
        return dict(id=old['id'], created_at=old['created_at'], **data)
    def evidence(profile_id, review_id):
        review = require('reviews', review_id)
        projection = require('projections', review['projection_id'])
        if projection['profile_id'] != profile_id:
            raise ValueError('evidence belongs to another profile')
        return review
    def lesson_state(item):
        expiry = item.get('review_after')
        if item['status'] == 'retired':
            return 'retired'
        review = require('reviews', item['review_id'])
        newer = rows('reviews', 'projection_id', review['projection_id'])
        if any(r.get('supersedes') == item['review_id'] for r in newer):
            return 'needs_review'
        if item['status'] == 'needs_review' or (expiry and expiry <= today):
            return 'needs_review'
        return item['status']
    if op == 'lesson_update':
        consent(); old = require('lessons', text(p,'lesson_id'))
        changes = p.get('changes')
        if not isinstance(changes,dict) or not changes or not set(changes) <= {'status','review_after','context','text','approved'}:
            raise ValueError('invalid lesson changes')
        if 'status' in changes and changes['status'] not in ('temporary','recurring','needs_review','retired'):
            raise ValueError('invalid lesson status')
        if 'review_after' in changes: day(changes['review_after'])
        if 'text' in changes: text(changes,'text')
        if ('text' in changes or 'context' in changes) and changes.get('approved') is not True:
            changes = {**changes, 'approved': False}
        if 'approved' in changes and not isinstance(changes['approved'],bool):
            raise ValueError('approved must be boolean')
        result = update('lessons',old,changes)
        return dict(**result, effective_status=lesson_state(result))
    if op == 'experiment_review':
        consent(); old = require('experiments',text(p,'experiment_id'))
        performed = p.get('performed')
        if performed not in ('yes','partly','no'):
            raise ValueError('performed must be yes, partly or no')
        changes = dict(status='reviewed', performed=performed, result=text(p,'result'),
            next_step=text(p,'next_step'), reviewed_at=now)
        return update('experiments',old,changes)
    pid = text(p,'profile_id')
    profile = require('profiles',pid)
    if op == 'checkin_add':
        consent()
        start,end = day(text(p,'period_start')),day(text(p,'period_end'))
        if end < start or end > today:
            raise ValueError('check-in period must be ordered and not in the future (UTC dates)')
        return add('checkins',pid,dict(profile_id=pid,period_start=start,period_end=end,
            experience=text(p,'experience'),source=text(p,'source'),
            exposure='before_reveal' if p.get('before_reveal') is True else 'unknown_or_exposed'))
    if op == 'checkins':
        return rows('checkins','profile_id',pid)
    if op == 'blind_due':
        # Deliberately excludes hypothesis, basis, alias, star ratings and lesson text.
        projections = rows('projections','profile_id',pid)
        superseded = {r.get('supersedes') for r in projections}
        due = []
        for item in projections:
            reviews = rows('reviews','projection_id',item['id'])
            replaced = {r.get('supersedes') for r in reviews}
            active = [r for r in reviews if r['id'] not in replaced]
            if item['review_after'] <= today and item['id'] not in superseded and not any(r['outcome'] != 'unclear' for r in active):
                due.append(dict(id=item['id'],period_start=item['period_start'],period_end=item['period_end'],
                    prompt='Apa yang paling terasa pada periode ini? Apa yang berjalan mudah atau sulit?'))
        return due
    if op == 'lesson_add':
        consent()
        status = p.get('status','temporary')
        if status not in ('temporary','recurring','needs_review'):
            raise ValueError('invalid lesson status')
        review_after = day(text(p,'review_after'))
        review_id = text(p,'review_id'); evidence(pid,review_id)
        return add('lessons',pid,dict(profile_id=pid,review_id=review_id,text=text(p,'text'),
            context=text(p,'context'),status=status,review_after=review_after,approved=p.get('approved') is True,
            source=text(p,'source')))
    if op == 'lessons':
        return [dict(**r,effective_status=lesson_state(r)) for r in rows('lessons','profile_id',pid)]
    if op == 'experiment_add':
        consent()
        projection_id = p.get('projection_id')
        if projection_id and require('projections',projection_id)['profile_id'] != pid:
            raise ValueError('experiment belongs to another profile')
        start,end = day(text(p,'period_start')),day(text(p,'period_end'))
        if end < start: raise ValueError('invalid experiment period')
        return add('experiments',pid,dict(profile_id=pid,projection_id=projection_id,
            action=text(p,'action'),observation=text(p,'observation'),context=text(p,'context'),
            period_start=start,period_end=end,source=text(p,'source'),status='planned'))
    if op == 'experiments':
        return rows('experiments','profile_id',pid)
    if op == 'relation_add':
        consent()
        alternatives = p.get('alternatives')
        if not isinstance(alternatives,list) or len(alternatives) < 2:
            raise ValueError('provide at least two alternative explanations')
        allowed = {'hypothesis','would_support','would_weaken','clarifying_question'}
        for item in alternatives:
            if not isinstance(item,dict) or set(item) != allowed:
                raise ValueError('alternative must contain hypothesis, would_support, would_weaken, clarifying_question')
            for key in allowed: text(item,key)
        return add('relation_notes',pid,dict(profile_id=pid,observation=text(p,'observation'),
            source=text(p,'source'),context=text(p,'context'),alternatives=alternatives,
            helpful_communication=p.get('helpful_communication',''),
            warning='Owner perspective; possibilities, not facts about hidden motives.'))
    if op == 'relations':
        return rows('relation_notes','profile_id',pid)
    if op == 'widget_data':
        if profile['relationship'] != 'self':
            raise ValueError('widget only supports an explicitly selected self profile')
        # No user-authored/private strings leave this projection. Raw journals stay in app.
        lessons = rows('lessons','profile_id',pid)
        usable = [r for r in lessons if r['approved'] and lesson_state(r) in ('temporary','recurring')]
        experiments = rows('experiments','profile_id',pid)
        active = [r for r in experiments if r['status']=='planned' and r['period_start'] <= today <= r['period_end']]
        return dict(question='Apa yang paling terasa hari ini, sebelum membaca tafsir?',
            action='Coba satu langkah kecil yang sudah kamu pilih.' if active else 'Pilih satu langkah kecil yang ada dalam kendalimu.',
            lesson='Ada pelajaran yang kamu setujui; lihat di aplikasi.' if usable else 'Belum ada pelajaran aktif yang disetujui.',
            lesson_id=usable[-1]['id'] if usable else None,
            experiment_id=active[-1]['id'] if active else None,
            privacy='generic_text_only',capture_url='astron://capture')
    raise ValueError('unknown reflection operation')
