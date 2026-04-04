#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/partner-campaign')
DB_PATH = BASE / 'data' / 'partner_campaign.db'

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
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def read_payload(path: Path) -> dict:
    return json.loads(path.read_text())


def pick_event_type(payload: dict) -> str:
    raw = str(payload.get('event') or payload.get('type') or '').strip().lower()
    return EVENT_MAP.get(raw, raw or 'unknown')


def pick_email(payload: dict) -> str | None:
    for key in ('email', 'recipient', 'contact_email'):
        value = payload.get(key)
        if value:
            return str(value).strip().lower()
    return None


def pick_campaign(payload: dict) -> str | None:
    for key in ('campaign_id', 'campaignId', 'campaign'):
        value = payload.get(key)
        if value is not None:
            return str(value)
    return None


def pick_ts(payload: dict) -> str:
    for key in ('ts', 'date', 'event_ts', 'created_at'):
        value = payload.get(key)
        if value:
            return str(value)
    return utc_now()


def main() -> None:
    parser = argparse.ArgumentParser(description='Ingest a Brevo webhook payload file into partner campaign DB')
    parser.add_argument('payload_file')
    args = parser.parse_args()

    payload_path = Path(args.payload_file)
    payload = read_payload(payload_path)
    event_type = pick_event_type(payload)
    email = pick_email(payload)
    campaign_ref = pick_campaign(payload)
    event_ts = pick_ts(payload)
    now = utc_now()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    lead = conn.execute('SELECT * FROM leads WHERE lower(email) = lower(?)', (email,)).fetchone() if email else None
    campaign = conn.execute('SELECT * FROM campaigns WHERE brevo_campaign_id = ?', (campaign_ref,)).fetchone() if campaign_ref else None

    lead_campaign = None
    if lead and campaign:
        lead_campaign = conn.execute(
            'SELECT * FROM lead_campaigns WHERE lead_id = ? AND campaign_id = ?',
            (lead['id'], campaign['id'])
        ).fetchone()
        if not lead_campaign:
            conn.execute(
                'INSERT INTO lead_campaigns (lead_id, campaign_id, send_status, created_at, updated_at) VALUES (?, ?, ?, ?, ?)',
                (lead['id'], campaign['id'], 'sent', now, now)
            )
            lead_campaign = conn.execute(
                'SELECT * FROM lead_campaigns WHERE lead_id = ? AND campaign_id = ?',
                (lead['id'], campaign['id'])
            ).fetchone()

    conn.execute(
        'INSERT INTO events (event_type, brevo_event_id, lead_id, campaign_id, lead_campaign_id, email, event_ts, raw_payload, meta_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (
            event_type,
            str(payload.get('id') or payload.get('event_id') or ''),
            lead['id'] if lead else None,
            campaign['id'] if campaign else None,
            lead_campaign['id'] if lead_campaign else None,
            email,
            event_ts,
            json.dumps(payload, ensure_ascii=False),
            json.dumps({'matched_lead': bool(lead), 'matched_campaign': bool(campaign)}, ensure_ascii=False),
            now,
        )
    )

    if lead:
        status = lead['status']
        do_not_contact = lead['do_not_contact']
        unsubscribed = lead['unsubscribed']
        bounced = lead['bounced']
        replied = lead['replied']

        if event_type == 'unsubscribe':
            status = 'unsubscribed'
            do_not_contact = 1
            unsubscribed = 1
        elif event_type in {'hard_bounce', 'soft_bounce'}:
            status = 'bounced'
            bounced = 1
            if event_type == 'hard_bounce':
                do_not_contact = 1
        elif event_type == 'reply':
            status = 'replied'
            replied = 1
        elif event_type in {'opened', 'clicked'} and status in {'new', 'validated', 'queued_for_campaign', 'sent'}:
            status = 'engaged'

        conn.execute(
            'UPDATE leads SET status = ?, do_not_contact = ?, unsubscribed = ?, bounced = ?, replied = ?, last_activity_at = ?, updated_at = ? WHERE id = ?',
            (status, do_not_contact, unsubscribed, bounced, replied, event_ts, now, lead['id'])
        )

    if lead_campaign:
        lc = dict(lead_campaign)
        open_count = lc.get('open_count', 0) or 0
        unique_open_count = lc.get('unique_open_count', 0) or 0
        click_count = lc.get('click_count', 0) or 0
        unique_click_count = lc.get('unique_click_count', 0) or 0
        reply_count = lc.get('reply_count', 0) or 0
        unsubscribe_count = lc.get('unsubscribe_count', 0) or 0
        bounce_count = lc.get('bounce_count', 0) or 0
        send_status = lc.get('send_status', 'queued')
        first_open_at = lc.get('first_open_at')
        last_open_at = lc.get('last_open_at')
        sent_at = lc.get('sent_at')

        if event_type == 'delivered':
            send_status = 'delivered'
            sent_at = sent_at or event_ts
        elif event_type == 'opened':
            open_count += 1
            unique_open_count += 1
            first_open_at = first_open_at or event_ts
            last_open_at = event_ts
        elif event_type == 'clicked':
            click_count += 1
            unique_click_count += 1
        elif event_type == 'reply':
            reply_count += 1
        elif event_type == 'unsubscribe':
            unsubscribe_count += 1
        elif event_type in {'hard_bounce', 'soft_bounce'}:
            bounce_count += 1

        conn.execute(
            '''UPDATE lead_campaigns SET send_status = ?, sent_at = ?, first_open_at = ?, last_open_at = ?,
               open_count = ?, unique_open_count = ?, click_count = ?, unique_click_count = ?,
               reply_count = ?, unsubscribe_count = ?, bounce_count = ?, last_event_at = ?, updated_at = ?
               WHERE id = ?''',
            (send_status, sent_at, first_open_at, last_open_at, open_count, unique_open_count, click_count,
             unique_click_count, reply_count, unsubscribe_count, bounce_count, event_ts, now, lead_campaign['id'])
        )

    conn.commit()
    conn.close()
    print(f'Ingested event type={event_type} email={email} campaign={campaign_ref}')


if __name__ == '__main__':
    main()
