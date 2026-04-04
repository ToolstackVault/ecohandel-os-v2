#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sqlite3
import subprocess
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/partner-campaign')
DB_PATH = BASE / 'data' / 'partner_campaign.db'
ACCESS_LOG = '/var/log/apache2/control.ecohandel-access.log'
CLICK_RE = re.compile(r'\[(?P<ts>[^\]]+)\]\s+"GET\s+(?P<path>/partners/p/[^\s"]+)')
TS_FMT = '%d/%b/%Y:%H:%M:%S %z'


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def fetch_remote_lines() -> list[str]:
    cmd = [
        'ssh', 'root@135.181.148.220',
        "(grep -h '/partners/p/' /var/log/apache2/control.ecohandel-access.log /var/log/apache2/control.ecohandel-access.log.1 2>/dev/null; zgrep -h '/partners/p/' /var/log/apache2/control.ecohandel-access.log.*.gz 2>/dev/null) || true"
    ]
    out = subprocess.check_output(cmd, text=True)
    return [line.strip() for line in out.splitlines() if '/partners/p/' in line and 'cid=' in line]


def parse_line(line: str) -> dict | None:
    match = CLICK_RE.search(line)
    if not match:
        return None
    raw_ts = match.group('ts')
    raw_path = match.group('path')
    try:
        event_ts = datetime.strptime(raw_ts, TS_FMT).astimezone(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    except Exception:
        event_ts = utc_now()

    parsed = urllib.parse.urlparse(raw_path)
    qs = urllib.parse.parse_qs(parsed.query)
    email = (qs.get('cid') or [''])[0].strip().lower()
    campaign = (qs.get('utm_campaign') or [''])[0].strip() or None
    if not email:
        return None
    return {
        'brevo_event_id': f'accesslog:{event_ts}:{email}:{campaign or "direct"}:{parsed.path}',
        'email': email,
        'campaign': campaign,
        'event_ts': event_ts,
        'path': parsed.path,
        'query': {k: v[0] if isinstance(v, list) and v else v for k, v in qs.items()},
        'raw_line': line,
    }


def ensure_campaign(conn: sqlite3.Connection, campaign_ref: str | None, now: str) -> sqlite3.Row | None:
    if not campaign_ref:
        return None
    row = conn.execute('SELECT * FROM campaigns WHERE brevo_campaign_id = ? OR name = ? LIMIT 1', (campaign_ref, campaign_ref)).fetchone()
    if row:
        return row
    conn.execute(
        '''INSERT INTO campaigns (brevo_campaign_id, name, campaign_type, subject_line, sender_name, sender_email, status, price_list_url, notes, created_at, updated_at)
           VALUES (?, ?, 'partner-outreach', 'Auto-created from prijslijst click ingest', 'EcoHandel.nl', 'info@ecohandel.nl', 'active', ?, ?, ?, ?)''',
        (campaign_ref, campaign_ref, 'https://control.ecohandel.nl/partners/p/a7x9kQ3m/', 'Auto-created from VPS access log click ingest', now, now)
    )
    return conn.execute('SELECT * FROM campaigns WHERE id = last_insert_rowid()').fetchone()


def guess_company_name(email: str) -> str:
    local = email.split('@', 1)[-1].split('.', 1)[0] if '@' in email else email
    return local.replace('-', ' ').replace('_', ' ').strip().title() or email


def ensure_lead(conn: sqlite3.Connection, email: str, now: str) -> sqlite3.Row:
    row = conn.execute('SELECT * FROM leads WHERE lower(email) = lower(?) LIMIT 1', (email,)).fetchone()
    if row:
        return row
    conn.execute(
        '''INSERT INTO leads (company_name, email, source, notes, source_date, segment, status, assigned_owner, lead_score, hot_score, last_activity_at, created_at, updated_at)
           VALUES (?, ?, 'partner_click_ingest', 'Auto-created from prijslijst click access log', ?, 'installer', 'engaged', 'Jean', 0, 0, ?, ?, ?)''',
        (guess_company_name(email), email, now[:10], now, now, now)
    )
    return conn.execute('SELECT * FROM leads WHERE id = last_insert_rowid()').fetchone()


def ensure_lead_campaign(conn: sqlite3.Connection, lead_id: int, campaign_id: int, event_ts: str, now: str) -> sqlite3.Row:
    row = conn.execute('SELECT * FROM lead_campaigns WHERE lead_id = ? AND campaign_id = ? LIMIT 1', (lead_id, campaign_id)).fetchone()
    if row:
        return row
    conn.execute(
        '''INSERT INTO lead_campaigns (lead_id, campaign_id, send_status, sent_at, last_event_at, created_at, updated_at)
           VALUES (?, ?, 'sent', ?, ?, ?, ?)''',
        (lead_id, campaign_id, event_ts, event_ts, now, now)
    )
    return conn.execute('SELECT * FROM lead_campaigns WHERE id = last_insert_rowid()').fetchone()


def main() -> None:
    now = utc_now()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    imported = 0
    skipped = 0
    unmatched = 0

    for line in fetch_remote_lines():
        payload = parse_line(line)
        if not payload:
            skipped += 1
            continue

        exists = conn.execute(
            "SELECT 1 FROM events WHERE event_type = 'clicked' AND brevo_event_id = ? LIMIT 1",
            (payload['brevo_event_id'],)
        ).fetchone()
        if exists:
            skipped += 1
            continue

        lead = ensure_lead(conn, payload['email'], now)
        if not lead:
            unmatched += 1
            continue

        campaign = ensure_campaign(conn, payload.get('campaign'), now)
        lead_campaign = None
        if campaign:
            lead_campaign = ensure_lead_campaign(conn, lead['id'], campaign['id'], payload['event_ts'], now)
            conn.execute(
                '''UPDATE lead_campaigns
                   SET click_count = COALESCE(click_count, 0) + 1,
                       unique_click_count = COALESCE(unique_click_count, 0) + 1,
                       last_event_at = ?,
                       updated_at = ?
                   WHERE id = ?''',
                (payload['event_ts'], now, lead_campaign['id'])
            )

        new_status = lead['status']
        if new_status in {'new', 'validated', 'queued_for_campaign', 'sent'}:
            new_status = 'engaged'
        conn.execute(
            '''UPDATE leads
               SET status = ?, last_activity_at = ?, updated_at = ?
               WHERE id = ?''',
            (new_status, payload['event_ts'], now, lead['id'])
        )

        conn.execute(
            '''INSERT INTO events (event_type, brevo_event_id, lead_id, campaign_id, lead_campaign_id, email, event_ts, raw_payload, meta_json, created_at)
               VALUES ('clicked', ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                payload['brevo_event_id'],
                lead['id'],
                campaign['id'] if campaign else None,
                lead_campaign['id'] if lead_campaign else None,
                payload['email'],
                payload['event_ts'],
                json.dumps(payload, ensure_ascii=False),
                json.dumps({'link_type': 'price_list', 'source': 'apache_access_log', 'campaign': payload.get('campaign')}, ensure_ascii=False),
                now,
            )
        )
        imported += 1

    conn.commit()
    conn.close()
    print(json.dumps({'imported': imported, 'skipped': skipped, 'unmatched': unmatched}, ensure_ascii=False))


if __name__ == '__main__':
    main()
