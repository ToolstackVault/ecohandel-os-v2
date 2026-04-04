#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/partner-campaign')
DB_PATH = BASE / 'data' / 'partner_campaign.db'
CONFIG_PATH = BASE / 'daily_send_config.json'
LAUNCH_ROOT = BASE / 'launch' / 'daily'


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding='utf-8'))


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def slot_priority_expr(variant: str) -> str:
    if variant == 'A':
        return """
        CASE WHEN upper(coalesce(warmth,'')) LIKE '%WARM%' THEN 3
             WHEN upper(coalesce(warmth,'')) LIKE '%MIDDEL%' THEN 2
             ELSE 1 END DESC,
        CASE WHEN upper(coalesce(deye_knowledge,'')) LIKE '%JA%' OR upper(coalesce(deye_knowledge,'')) LIKE '%DEYE%' THEN 1 ELSE 0 END DESC,
        CASE WHEN upper(coalesce(battery_experience,'')) LIKE '%JA%' THEN 1 ELSE 0 END DESC,
        lead_score DESC,
        hot_score DESC,
        id ASC
        """
    return """
        CASE WHEN upper(coalesce(battery_experience,'')) LIKE '%JA%' THEN 1 ELSE 0 END DESC,
        CASE WHEN upper(coalesce(warmth,'')) LIKE '%WARM%' THEN 2
             WHEN upper(coalesce(warmth,'')) LIKE '%MIDDEL%' THEN 1
             ELSE 0 END DESC,
        lead_score DESC,
        hot_score DESC,
        id ASC
    """


def build_where_clauses(cfg: dict) -> tuple[str, list[str]]:
    clauses = [
        "coalesce(email, '') <> ''",
        "lower(coalesce(email,'')) NOT LIKE '%test@%'",
        "lower(coalesce(email,'')) NOT LIKE '%example.com%'",
        "lower(coalesce(email,'')) NOT LIKE '%{{contact.%'",
        "lower(coalesce(email,'')) NOT LIKE '%@ecohandel.nl'",
        "lower(coalesce(email,'')) NOT LIKE '%@gmail.com'",
        "lower(coalesce(email,'')) NOT LIKE '%@hotmail.com'",
        "lower(coalesce(email,'')) NOT LIKE '%@outlook.com'",
        "do_not_contact = 0",
        "unsubscribed = 0",
        "bounced = 0",
        "lower(coalesce(status,'')) NOT IN ('replied','unsubscribed','bounced')",
        "lower(coalesce(company_name,'')) NOT LIKE '%test%'",
        "lower(coalesce(company_name,'')) NOT LIKE '%ecohandel%'",
        "lower(coalesce(company_name,'')) NOT LIKE '%bekend contact%'",
        "NOT EXISTS (SELECT 1 FROM lead_campaigns lc WHERE lc.lead_id = leads.id AND lc.send_status IN ('queued','ready','sent'))"
    ]
    params: list[str] = []

    for pattern in cfg.get('exclude_company_patterns', []):
        clauses.append("lower(coalesce(company_name,'')) NOT LIKE ?")
        params.append(f"%{pattern.lower()}%")

    for pattern in cfg.get('exclude_email_patterns', []):
        clauses.append("lower(coalesce(email,'')) NOT LIKE ?")
        params.append(f"%{pattern.lower()}%")

    return " AND ".join(clauses), params


def pick_rows(conn: sqlite3.Connection, cfg: dict, variant: str, count: int, already_picked_ids: set[int]) -> list[sqlite3.Row]:
    where_sql, params = build_where_clauses(cfg)
    extra = ""
    if already_picked_ids:
        placeholders = ','.join('?' for _ in already_picked_ids)
        extra = f" AND id NOT IN ({placeholders})"
        params.extend(str(x) for x in already_picked_ids)

    query = f"""
        SELECT id, company_name, province, website, phone, email, contact_person, role,
               battery_experience, deye_knowledge, warmth, source, notes, segment,
               lead_score, hot_score, status
        FROM leads
        WHERE {where_sql}{extra}
        ORDER BY {slot_priority_expr(variant)}
        LIMIT ?
    """
    params.append(str(count))
    return conn.execute(query, params).fetchall()


def write_csv(path: Path, rows: list[sqlite3.Row], batch_key: str) -> None:
    fieldnames = [
        'batch', 'rank', 'company_name', 'email', 'phone', 'website', 'province',
        'contact_person', 'warmth', 'deye_knowledge', 'battery_experience',
        'lead_score', 'hot_score', 'segment', 'notes'
    ]
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for idx, row in enumerate(rows, start=1):
            writer.writerow({
                'batch': batch_key,
                'rank': idx,
                'company_name': row['company_name'],
                'email': row['email'],
                'phone': row['phone'],
                'website': row['website'],
                'province': row['province'],
                'contact_person': row['contact_person'],
                'warmth': row['warmth'],
                'deye_knowledge': row['deye_knowledge'],
                'battery_experience': row['battery_experience'],
                'lead_score': row['lead_score'],
                'hot_score': row['hot_score'],
                'segment': row['segment'],
                'notes': row['notes'],
            })


def main() -> int:
    cfg = load_config()
    tz = ZoneInfo(cfg.get('timezone', 'Europe/Amsterdam'))
    today = datetime.now(tz).date().isoformat()
    out_dir = LAUNCH_ROOT / today
    ensure_dir(out_dir)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    schedule = {
        'date': today,
        'timezone': cfg.get('timezone', 'Europe/Amsterdam'),
        'status': 'generated',
        'goal': 'Daily repeatable partner campaign schedule',
        'source_config': str(CONFIG_PATH.relative_to(BASE)),
        'batches': []
    }

    picked_ids: set[int] = set()
    for slot in cfg.get('slots', []):
        variant = slot['variant']
        count = int(slot['count'])
        send_time = slot['send_time']
        hh, mm = send_time.split(':', 1)
        batch_key = slot['key']
        campaign_key = f"partner-daily-{today}-{batch_key.lower()}"
        csv_name = f"{batch_key}.csv"
        rows = pick_rows(conn, cfg, variant, count, picked_ids)
        picked_ids.update(int(r['id']) for r in rows)
        write_csv(out_dir / csv_name, rows, batch_key)
        subject = (
            'Partner worden voor Deye systemen? Bekijk onze prijslijst'
            if variant == 'A' else
            'Deye partnerprijzen voor installateurs — direct inzicht'
        )
        schedule['batches'].append({
            'batch': batch_key,
            'send_at': f'{today}T{hh}:{mm}:00',
            'variant': variant,
            'subject': subject,
            'campaign_key': campaign_key,
            'csv_file': csv_name,
            'count_requested': count,
            'count_selected': len(rows),
            'label': slot.get('label', '')
        })

    (out_dir / 'schedule.json').write_text(json.dumps(schedule, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'ok': True, 'date': today, 'dir': str(out_dir), 'batches': schedule['batches']}, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
