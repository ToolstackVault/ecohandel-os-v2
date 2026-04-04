#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/partner-campaign')
CONFIG = json.loads((BASE / 'config.local.json').read_text(encoding='utf-8'))
DB_PATH = BASE / 'data' / 'partner_campaign.db'
API_KEY = CONFIG['brevo']['api_key']
EVENT_MAP = {
    'delivered': 'delivered',
    'opened': 'opened',
    'open': 'opened',
    'clicked': 'clicked',
    'click': 'clicked',
    'hard_bounce': 'hard_bounce',
    'soft_bounce': 'soft_bounce',
    'unsubscribe': 'unsubscribe',
    'unsubscribed': 'unsubscribe',
    'reply': 'reply',
    'error': 'error',
    'requests': 'requests',
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def brevo_get(path: str, query: dict | None = None) -> dict:
    url = 'https://api.brevo.com/v3' + path
    if query:
        url += '?' + urllib.parse.urlencode(query)
    req = urllib.request.Request(url, headers={'accept': 'application/json', 'api-key': API_KEY})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode('utf-8') or '{}')


def fetch_events(days: int = 14) -> list[dict]:
    start_date = (datetime.now(timezone.utc).date() - timedelta(days=days)).isoformat()
    end_date = datetime.now(timezone.utc).date().isoformat()
    offset = 0
    events: list[dict] = []
    while True:
        payload = brevo_get('/smtp/statistics/events', {
            'limit': 500,
            'offset': offset,
            'startDate': start_date,
            'endDate': end_date,
        })
        batch = payload.get('events', []) if isinstance(payload, dict) else []
        if not batch:
            break
        events.extend(batch)
        if len(batch) < 500:
            break
        offset += 500
    return events


def normalize_event(raw: dict) -> dict:
    ev = EVENT_MAP.get(str(raw.get('event') or '').lower().strip(), str(raw.get('event') or '').lower().strip() or 'unknown')
    email = str(raw.get('email') or '').strip().lower()
    tag = str(raw.get('tag') or '').strip() or None
    event_ts = str(raw.get('date') or raw.get('event_ts') or utc_now())
    msg_id = str(raw.get('messageId') or '')
    reason = str(raw.get('reason') or '')
    event_id = f"brevo:{ev}:{msg_id}:{email}:{tag or 'untagged'}:{event_ts}"
    return {
        'event_type': ev,
        'brevo_event_id': event_id,
        'email': email,
        'campaign_ref': tag,
        'event_ts': event_ts,
        'raw_payload': raw,
        'reason': reason,
    }


def ensure_lead(conn: sqlite3.Connection, email: str, now: str) -> sqlite3.Row | None:
    if not email:
        return None
    row = conn.execute('SELECT * FROM leads WHERE lower(email) = lower(?) LIMIT 1', (email,)).fetchone()
    if row:
        return row
    return None


def ensure_campaign(conn: sqlite3.Connection, campaign_ref: str | None) -> sqlite3.Row | None:
    if not campaign_ref:
        return None
    return conn.execute(
        'SELECT * FROM campaigns WHERE brevo_campaign_id = ? OR name = ? LIMIT 1',
        (campaign_ref, campaign_ref)
    ).fetchone()


def ensure_lead_campaign(conn: sqlite3.Connection, lead_id: int, campaign_id: int, event_ts: str, now: str) -> sqlite3.Row:
    row = conn.execute('SELECT * FROM lead_campaigns WHERE lead_id = ? AND campaign_id = ? LIMIT 1', (lead_id, campaign_id)).fetchone()
    if row:
        return row
    conn.execute(
        '''INSERT INTO lead_campaigns (lead_id, campaign_id, send_status, sent_at, last_event_at, created_at, updated_at)
           VALUES (?, ?, 'sent', ?, ?, ?, ?)''',
        (lead_id, campaign_id, event_ts if 'T' in event_ts else now, event_ts if 'T' in event_ts else now, now, now)
    )
    return conn.execute('SELECT * FROM lead_campaigns WHERE id = last_insert_rowid()').fetchone()


def main() -> None:
    events = [normalize_event(e) for e in fetch_events(14)]
    now = utc_now()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    imported = 0
    skipped = 0
    unmatched = 0

    for item in events:
        if item['event_type'] not in {'delivered', 'opened', 'clicked', 'hard_bounce', 'soft_bounce', 'unsubscribe', 'reply', 'error'}:
            skipped += 1
            continue
        exists = conn.execute('SELECT 1 FROM events WHERE brevo_event_id = ? LIMIT 1', (item['brevo_event_id'],)).fetchone()
        if exists:
            skipped += 1
            continue

        lead = ensure_lead(conn, item['email'], now)
        campaign = ensure_campaign(conn, item['campaign_ref'])
        lead_campaign = None
        if lead and campaign:
            lead_campaign = ensure_lead_campaign(conn, lead['id'], campaign['id'], item['event_ts'], now)
        elif not lead:
            unmatched += 1

        meta = {
            'campaign_ref': item['campaign_ref'],
            'reason': item['reason'],
            'source': 'brevo_smtp_events',
        }
        conn.execute(
            '''INSERT INTO events (event_type, brevo_event_id, lead_id, campaign_id, lead_campaign_id, email, event_ts, raw_payload, meta_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                item['event_type'], item['brevo_event_id'],
                lead['id'] if lead else None,
                campaign['id'] if campaign else None,
                lead_campaign['id'] if lead_campaign else None,
                item['email'] or None,
                item['event_ts'],
                json.dumps(item['raw_payload'], ensure_ascii=False),
                json.dumps(meta, ensure_ascii=False),
                now,
            )
        )

        if lead_campaign:
            lc = dict(lead_campaign)
            updates = {
                'send_status': lc.get('send_status', 'queued'),
                'sent_at': lc.get('sent_at'),
                'first_open_at': lc.get('first_open_at'),
                'last_open_at': lc.get('last_open_at'),
                'open_count': lc.get('open_count', 0) or 0,
                'unique_open_count': lc.get('unique_open_count', 0) or 0,
                'click_count': lc.get('click_count', 0) or 0,
                'unique_click_count': lc.get('unique_click_count', 0) or 0,
                'reply_count': lc.get('reply_count', 0) or 0,
                'unsubscribe_count': lc.get('unsubscribe_count', 0) or 0,
                'bounce_count': lc.get('bounce_count', 0) or 0,
                'last_event_at': item['event_ts'],
            }
            ev = item['event_type']
            if ev == 'delivered':
                updates['send_status'] = 'delivered'
                updates['sent_at'] = updates['sent_at'] or item['event_ts']
            elif ev == 'opened':
                updates['open_count'] += 1
                updates['unique_open_count'] += 1
                updates['first_open_at'] = updates['first_open_at'] or item['event_ts']
                updates['last_open_at'] = item['event_ts']
            elif ev == 'clicked':
                updates['click_count'] += 1
                updates['unique_click_count'] += 1
            elif ev == 'reply':
                updates['reply_count'] += 1
            elif ev == 'unsubscribe':
                updates['unsubscribe_count'] += 1
            elif ev in {'hard_bounce', 'soft_bounce'}:
                updates['bounce_count'] += 1

            conn.execute(
                '''UPDATE lead_campaigns SET send_status = ?, sent_at = ?, first_open_at = ?, last_open_at = ?,
                   open_count = ?, unique_open_count = ?, click_count = ?, unique_click_count = ?,
                   reply_count = ?, unsubscribe_count = ?, bounce_count = ?, last_event_at = ?, updated_at = ?
                   WHERE id = ?''',
                (
                    updates['send_status'], updates['sent_at'], updates['first_open_at'], updates['last_open_at'],
                    updates['open_count'], updates['unique_open_count'], updates['click_count'], updates['unique_click_count'],
                    updates['reply_count'], updates['unsubscribe_count'], updates['bounce_count'], updates['last_event_at'], now,
                    lead_campaign['id']
                )
            )

        if lead:
            status = lead['status']
            do_not_contact = lead['do_not_contact']
            unsubscribed = lead['unsubscribed']
            bounced = lead['bounced']
            replied = lead['replied']
            if item['event_type'] == 'unsubscribe':
                status = 'unsubscribed'
                do_not_contact = 1
                unsubscribed = 1
            elif item['event_type'] in {'hard_bounce', 'soft_bounce'}:
                status = 'bounced'
                bounced = 1
                if item['event_type'] == 'hard_bounce':
                    do_not_contact = 1
            elif item['event_type'] == 'reply':
                status = 'replied'
                replied = 1
            elif item['event_type'] in {'opened', 'clicked', 'delivered'} and status in {'new', 'validated', 'queued_for_campaign', 'sent'}:
                status = 'engaged'
            conn.execute(
                'UPDATE leads SET status = ?, do_not_contact = ?, unsubscribed = ?, bounced = ?, replied = ?, last_activity_at = ?, updated_at = ? WHERE id = ?',
                (status, do_not_contact, unsubscribed, bounced, replied, item['event_ts'], now, lead['id'])
            )
        imported += 1

    conn.commit()
    conn.close()
    print(json.dumps({'imported': imported, 'skipped': skipped, 'unmatched': unmatched, 'fetched': len(events)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
