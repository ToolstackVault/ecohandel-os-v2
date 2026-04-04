#!/usr/bin/env python3
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/partner-campaign')
DB_PATH = BASE / 'data' / 'partner_campaign.db'


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def parse_iso(v: str | None):
    if not v:
        return None
    try:
        return datetime.fromisoformat(v.replace('Z', '+00:00'))
    except Exception:
        return None


def fit_score(row: sqlite3.Row) -> int:
    score = 0
    warmth = (row['warmth'] or '').upper()
    if 'WARM' in warmth and 'MIDDEL' not in warmth:
        score += 25
    elif 'MIDDEL-WARM' in warmth:
        score += 18
    elif 'MIDDEL' in warmth:
        score += 10

    deye = (row['deye_knowledge'] or '').upper()
    if 'JA' in deye or 'DEYE' in deye:
        score += 20
    elif 'ONBEKEND' in deye:
        score += 5

    battery = (row['battery_experience'] or '').upper()
    if 'ZAKELIJK' in battery:
        score += 18
    elif battery:
        score += 15

    if row['email']:
        score += 10
    if row['phone']:
        score += 8
    if row['contact_person']:
        score += 8

    website = (row['website'] or '').lower()
    notes = (row['notes'] or '').lower()
    province = (row['province'] or '').lower()
    if 'landelijk' in notes or 'landelijk' in province:
        score += 10
    if any(x in notes for x in ['zakelijke', 'netcongestie', 'wholesale', 'partner']):
        score += 12
    if website:
        score += 2
    return score


def hot_score(row: sqlite3.Row, agg: sqlite3.Row | None) -> int:
    score = 0
    if not agg:
        return score
    score += int(agg['delivered_count'] or 0) * 1
    opens = int(agg['open_count'] or 0)
    clicks = int(agg['click_count'] or 0)
    replies = int(agg['reply_count'] or 0)
    price_clicks = int(agg['price_list_clicks'] or 0)
    product_clicks = int(agg['product_clicks'] or 0)
    cta_clicks = int(agg['cta_clicks'] or 0)
    partner_requests = int(agg['partner_requests'] or 0)

    if opens > 0:
        score += 3 + max(0, opens - 1) * 2
    score += clicks * 7
    score += price_clicks * 18
    score += product_clicks * 22
    score += cta_clicks * 12
    if product_clicks >= 2:
        score += 15
    score += replies * 45
    score += partner_requests * 60
    if row['replied']:
        score += 25

    last_activity = parse_iso(row['last_activity_at'])
    now = datetime.now(timezone.utc)
    if last_activity:
        if last_activity >= now - timedelta(days=1):
            score += 20
        elif last_activity >= now - timedelta(days=3):
            score += 12
        elif last_activity >= now - timedelta(days=7):
            score += 5

    if row['unsubscribed']:
        score -= 100
    if row['bounced']:
        score -= 120
    return score


def derive_status(row: sqlite3.Row, hot: int, agg: sqlite3.Row | None) -> str:
    if row['unsubscribed']:
        return 'unsubscribed'
    if row['bounced']:
        return 'bounced'
    if agg and int(agg['partner_requests'] or 0) > 0:
        return 'hot'
    if row['replied'] or (agg and int(agg['reply_count'] or 0) > 0):
        return 'replied'
    if hot >= 60:
        return 'hot'
    if agg and (int(agg['open_count'] or 0) > 0 or int(agg['click_count'] or 0) > 0):
        return 'engaged'
    return row['status'] or 'validated'


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    leads = conn.execute('SELECT * FROM leads').fetchall()
    now = utc_now()

    for lead in leads:
        agg = conn.execute(
            '''SELECT
                 SUM(CASE WHEN send_status IN ('delivered','sent') THEN 1 ELSE 0 END) AS delivered_count,
                 SUM(open_count) AS open_count,
                 SUM(click_count) AS click_count,
                 SUM(reply_count) AS reply_count,
                 SUM(CASE WHEN id IN (
                     SELECT lead_campaign_id FROM events WHERE event_type='clicked' AND json_extract(meta_json, '$.link_type')='price_list'
                 ) THEN 1 ELSE 0 END) AS price_list_clicks,
                 SUM(CASE WHEN id IN (
                     SELECT lead_campaign_id FROM events WHERE event_type='clicked' AND json_extract(meta_json, '$.link_type')='product'
                 ) THEN 1 ELSE 0 END) AS product_clicks,
                 SUM(CASE WHEN id IN (
                     SELECT lead_campaign_id FROM events WHERE event_type='cta_click'
                 ) THEN 1 ELSE 0 END) AS cta_clicks,
                 SUM(CASE WHEN id IN (
                     SELECT lead_campaign_id FROM events WHERE event_type='partner_request'
                 ) THEN 1 ELSE 0 END) AS partner_requests
               FROM lead_campaigns WHERE lead_id = ?''',
            (lead['id'],)
        ).fetchone()

        leadscore = fit_score(lead)
        hotscore = hot_score(lead, agg)
        status = derive_status(lead, hotscore, agg)
        conn.execute(
            'UPDATE leads SET lead_score = ?, hot_score = ?, status = ?, updated_at = ? WHERE id = ?',
            (leadscore, hotscore, status, now, lead['id'])
        )

    conn.commit()
    conn.close()
    print('Recalculated lead_score and hot_score for all leads')


if __name__ == '__main__':
    main()
