#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/partner-campaign')
DB_PATH = BASE / 'data' / 'partner_campaign.db'
REPORTS_DIR = BASE / 'reports'


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def parse_iso(v: str | None):
    if not v:
        return None
    try:
        return datetime.fromisoformat(v.replace('Z', '+00:00'))
    except Exception:
        return None


def is_external_lead(email: str | None, company_name: str | None) -> bool:
    e = (email or '').strip().lower()
    c = (company_name or '').strip().lower()
    if not e or '{{' in e or '}}' in e:
        return False
    blocked_domains = ('@ecohandel.nl', '@nova-cell.com', '@dekeizonnepanelen.nl', '@outlook.com', '@hotmail.com', '@gmail.com')
    if e.endswith(blocked_domains):
        return False
    blocked_names = ('milan', 'bekend contact', 'ecohandel', 'nova-cell', 'de kei')
    if any(name in c for name in blocked_names):
        return False
    return True


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    hot = []
    rows = conn.execute(
        '''SELECT l.id, l.company_name, l.contact_person, l.email, l.phone, l.website, l.warmth,
                  l.status, l.replied, l.unsubscribed, l.bounced, l.last_activity_at,
                  COALESCE(SUM(lc.open_count),0) AS open_count,
                  COALESCE(SUM(lc.click_count),0) AS click_count,
                  COALESCE(SUM(lc.reply_count),0) AS reply_count
           FROM leads l
           LEFT JOIN lead_campaigns lc ON lc.lead_id = l.id
           WHERE l.do_not_contact = 0
           GROUP BY l.id
           ORDER BY reply_count DESC, click_count DESC, open_count DESC, l.company_name ASC'''
    ).fetchall()

    now = datetime.now(timezone.utc)
    for row in rows:
        if not is_external_lead(row['email'], row['company_name']):
            continue
        score = 0
        if row['warmth']:
            warmth = str(row['warmth']).upper()
            if 'WARM' in warmth:
                score += 25
            elif 'MIDDEL' in warmth:
                score += 10
        score += int(row['open_count'] or 0) * 3
        score += int(row['click_count'] or 0) * 10
        score += int(row['reply_count'] or 0) * 40
        if row['replied']:
            score += 25
        if row['unsubscribed']:
            score -= 80
        if row['bounced']:
            score -= 100
        last_activity = parse_iso(row['last_activity_at'])
        if last_activity and last_activity >= now - timedelta(days=3):
            score += 15

        action = 'NOG EVEN LATEN LOPEN'
        if row['replied'] or (row['reply_count'] or 0) > 0:
            action = 'BEL VANDAAG'
        elif (row['click_count'] or 0) >= 2:
            action = 'HANDMATIG MAILEN'
        elif (row['open_count'] or 0) >= 2:
            action = 'OPVOLGEN'

        if score >= 20:
            hot.append({
                'lead_id': row['id'],
                'company_name': row['company_name'],
                'contact_person': row['contact_person'],
                'email': row['email'],
                'phone': row['phone'],
                'website': row['website'],
                'warmth': row['warmth'],
                'status': row['status'],
                'open_count': row['open_count'],
                'click_count': row['click_count'],
                'reply_count': row['reply_count'],
                'score': score,
                'recommended_action': action,
                'last_activity_at': row['last_activity_at'],
            })

    hot = sorted(hot, key=lambda x: (-x['score'], x['company_name']))[:25]

    report = {
        'generated_at': utc_now(),
        'hot_count': len(hot),
        'hot_prospects': hot,
    }
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"hot-prospects-{datetime.now().strftime('%Y-%m-%d')}.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')

    conn.execute(
        'INSERT OR REPLACE INTO daily_reports (report_date, hot_count, replied_count, opened_count, clicked_count, unsubscribed_count, bounced_count, report_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (
            datetime.now().strftime('%Y-%m-%d'),
            len(hot),
            sum(int(x['reply_count'] or 0) for x in hot),
            sum(int(x['open_count'] or 0) for x in hot),
            sum(int(x['click_count'] or 0) for x in hot),
            0,
            0,
            json.dumps(report, ensure_ascii=False),
            utc_now(),
        ),
    )
    conn.commit()
    conn.close()

    print(f'Wrote {report_path}')
    print(f'Hot prospects: {len(hot)}')


if __name__ == '__main__':
    main()
