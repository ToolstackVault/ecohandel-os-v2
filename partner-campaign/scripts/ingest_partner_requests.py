#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/partner-campaign')
DB_PATH = BASE / 'data' / 'partner_campaign.db'
REMOTE_LOG = '/var/www/html/control.ecohandel.nl/data/partner-aanvragen.ndjson'


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def fetch_remote_log() -> list[dict]:
    cmd = [
        'ssh', 'root@135.181.148.220',
        f'cat {REMOTE_LOG} 2>/dev/null || true'
    ]
    out = subprocess.check_output(cmd, text=True)
    rows = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def ensure_campaign(conn: sqlite3.Connection, campaign_ref: str | None, now: str) -> sqlite3.Row | None:
    if not campaign_ref:
        return None
    row = conn.execute('SELECT * FROM campaigns WHERE brevo_campaign_id = ? OR name = ? LIMIT 1', (campaign_ref, campaign_ref)).fetchone()
    if row:
        return row
    conn.execute(
        '''INSERT INTO campaigns (brevo_campaign_id, name, campaign_type, subject_line, sender_name, sender_email, status, price_list_url, notes, created_at, updated_at)
           VALUES (?, ?, 'partner-outreach', 'Partner aanvraag via prijslijst', 'EcoHandel.nl', 'info@ecohandel.nl', 'active', ?, ?, ?, ?)''',
        (campaign_ref, campaign_ref, 'https://control.ecohandel.nl/partners/p/a7x9kQ3m/', 'Auto-created from partner request ingest', now, now)
    )
    return conn.execute('SELECT * FROM campaigns WHERE id = last_insert_rowid()').fetchone()


def ensure_lead(conn: sqlite3.Connection, payload: dict, now: str) -> sqlite3.Row:
    event_type = str(payload.get('event_type') or 'partner_request').strip().lower()
    email = (payload.get('email') or '').strip().lower()
    website = (payload.get('website') or '').strip().lower() or None
    lead = None
    if email:
        lead = conn.execute('SELECT * FROM leads WHERE lower(email) = lower(?) LIMIT 1', (email,)).fetchone()
    if not lead and website:
        lead = conn.execute('SELECT * FROM leads WHERE lower(website) = lower(?) LIMIT 1', (website,)).fetchone()

    status = 'engaged' if event_type == 'cta_click' else 'replied'
    replied_flag = 1 if event_type == 'partner_request' else 0
    note_label = 'CTA klik op partnerflow' if event_type == 'cta_click' else 'Partner aanvraag via prijslijst'

    if lead:
        conn.execute(
            '''UPDATE leads SET contact_person = COALESCE(NULLIF(?,''), contact_person),
                      phone = COALESCE(NULLIF(?,''), phone),
                      source = COALESCE(source, ?),
                      notes = COALESCE(notes, ?),
                      replied = CASE WHEN ? = 1 THEN 1 ELSE replied END,
                      status = ?,
                      last_activity_at = ?,
                      updated_at = ?
               WHERE id = ?''',
            (
                payload.get('naam', ''), payload.get('telefoon', ''),
                f"partner_{payload.get('bron') or 'formulier'}",
                f"{note_label} ({payload.get('campaign') or 'direct'})",
                replied_flag,
                status,
                payload.get('received_at') or now, now, lead['id']
            )
        )
        return conn.execute('SELECT * FROM leads WHERE id = ?', (lead['id'],)).fetchone()

    company_name = (payload.get('bedrijf') or payload.get('naam') or email or 'Onbekende partnerflow').strip()
    conn.execute(
        '''INSERT INTO leads (company_name, website, phone, email, contact_person, source, notes, source_date, segment, status, assigned_owner, replied, lead_score, hot_score, last_activity_at, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'installer', ?, 'Jean', ?, 0, 0, ?, ?, ?)''',
        (
            company_name,
            website,
            payload.get('telefoon'),
            email or None,
            payload.get('naam'),
            f"partner_{payload.get('bron') or 'formulier'}",
            f"{note_label} ({payload.get('campaign') or 'direct'})",
            (payload.get('received_at') or now)[:10],
            status,
            replied_flag,
            payload.get('received_at') or now,
            now,
            now,
        )
    )
    return conn.execute('SELECT * FROM leads WHERE id = last_insert_rowid()').fetchone()


def main() -> None:
    rows = fetch_remote_log()
    now = utc_now()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    imported = 0
    skipped = 0
    for payload in rows:
        request_id = str(payload.get('request_id') or '')
        if not request_id:
            skipped += 1
            continue

        event_type = str(payload.get('event_type') or 'partner_request').strip().lower()
        if event_type not in {'partner_request', 'cta_click'}:
            skipped += 1
            continue

        existing = conn.execute(
            "SELECT 1 FROM events WHERE event_type = ? AND brevo_event_id = ? LIMIT 1",
            (event_type, request_id)
        ).fetchone()
        if existing:
            skipped += 1
            continue

        campaign = ensure_campaign(conn, payload.get('campaign'), now)
        lead = ensure_lead(conn, payload, now)

        lead_campaign = None
        if lead and campaign:
            lead_campaign = conn.execute(
                'SELECT * FROM lead_campaigns WHERE lead_id = ? AND campaign_id = ? LIMIT 1',
                (lead['id'], campaign['id'])
            ).fetchone()
            if not lead_campaign:
                conn.execute(
                    '''INSERT INTO lead_campaigns (lead_id, campaign_id, send_status, sent_at, reply_count, last_event_at, created_at, updated_at)
                       VALUES (?, ?, 'sent', ?, ?, ?, ?, ?)''',
                    (
                        lead['id'], campaign['id'], payload.get('received_at') or now,
                        1 if event_type == 'partner_request' else 0,
                        payload.get('received_at') or now, now, now
                    )
                )
                lead_campaign = conn.execute('SELECT * FROM lead_campaigns WHERE id = last_insert_rowid()').fetchone()
            else:
                conn.execute(
                    '''UPDATE lead_campaigns
                       SET send_status='sent',
                           reply_count = COALESCE(reply_count,0) + ?,
                           last_event_at = ?,
                           updated_at = ?
                       WHERE id = ?''',
                    (1 if event_type == 'partner_request' else 0, payload.get('received_at') or now, now, lead_campaign['id'])
                )
                lead_campaign = conn.execute('SELECT * FROM lead_campaigns WHERE id = ?', (lead_campaign['id'],)).fetchone()

        if event_type == 'partner_request':
            conn.execute(
                '''INSERT INTO replies (lead_id, campaign_id, channel, direction, subject, message_preview, received_at, classification, sentiment, urgency, action_recommendation, raw_source, created_at, updated_at)
                   VALUES (?, ?, 'partner-form', 'inbound', ?, ?, ?, 'interested', 'positive', 'high', 'bel vandaag', ?, ?, ?)''',
                (
                    lead['id'],
                    campaign['id'] if campaign else None,
                    f"Partner aanvraag via prijslijst ({payload.get('campaign') or 'direct'})",
                    f"Naam: {payload.get('naam') or '—'} | Email: {payload.get('email') or '—'} | Telefoon: {payload.get('telefoon') or '—'} | Bron: {payload.get('bron') or '—'}",
                    payload.get('received_at') or now,
                    json.dumps(payload, ensure_ascii=False),
                    now,
                    now,
                )
            )

        conn.execute(
            '''INSERT INTO events (event_type, brevo_event_id, lead_id, campaign_id, lead_campaign_id, email, event_ts, raw_payload, meta_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                event_type,
                request_id,
                lead['id'],
                campaign['id'] if campaign else None,
                lead_campaign['id'] if lead_campaign else None,
                (payload.get('email') or '').strip().lower() or None,
                payload.get('received_at') or now,
                json.dumps(payload, ensure_ascii=False),
                json.dumps({'source': payload.get('bron'), 'campaign': payload.get('campaign'), 'matched_lead': True}, ensure_ascii=False),
                now,
            )
        )

        imported += 1

    conn.commit()
    conn.close()
    print(json.dumps({'imported': imported, 'skipped': skipped, 'remote_rows': len(rows)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
