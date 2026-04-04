#!/usr/bin/env python3
from __future__ import annotations

import csv
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/partner-campaign')
DB_PATH = BASE / 'data' / 'partner_campaign.db'
CSV_PATH = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/lead-generation/leads/LEADS.csv')


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def normalize(v: str) -> str | None:
    if v is None:
        return None
    v = v.strip()
    if not v or v.upper() == 'ONBEKEND':
        return None
    return v


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f'Database missing: {DB_PATH}. Run bootstrap_db.py first.')

    conn = sqlite3.connect(DB_PATH)
    inserted = 0
    updated = 0
    now = utc_now()

    with CSV_PATH.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = normalize(row.get('EMAIL', ''))
            website = normalize(row.get('WEBSITE', ''))
            company = normalize(row.get('BEDRIJF', ''))
            if not company:
                continue

            existing = conn.execute(
                'SELECT id FROM leads WHERE COALESCE(email, "") = COALESCE(?, "") AND COALESCE(website, "") = COALESCE(?, "")',
                (email, website),
            ).fetchone()

            payload = {
                'company_name': company,
                'province': normalize(row.get('PROVINCIE', '')),
                'website': website,
                'phone': normalize(row.get('TELEFOON', '')),
                'email': email,
                'contact_person': normalize(row.get('CONTACTPERSOON', '')),
                'role': normalize(row.get('FUNCTIE', '')),
                'battery_experience': normalize(row.get('BATTERIJ_ERVARING', '')),
                'deye_knowledge': normalize(row.get('DEYE_KENNIS', '')),
                'warmth': normalize(row.get('WARMTE', '')),
                'source': normalize(row.get('BRON', '')),
                'notes': normalize(row.get('NOTITIES', '')),
                'source_date': normalize(row.get('DATUM', '')),
                'segment': 'installer',
                'status': 'validated',
                'updated_at': now,
            }

            if existing:
                conn.execute(
                    '''UPDATE leads SET
                       company_name=:company_name, province=:province, website=:website, phone=:phone,
                       email=:email, contact_person=:contact_person, role=:role,
                       battery_experience=:battery_experience, deye_knowledge=:deye_knowledge,
                       warmth=:warmth, source=:source, notes=:notes, source_date=:source_date,
                       segment=:segment, status=:status, updated_at=:updated_at
                       WHERE id = :id''',
                    {**payload, 'id': existing[0]},
                )
                updated += 1
            else:
                conn.execute(
                    '''INSERT INTO leads (
                       company_name, province, website, phone, email, contact_person, role,
                       battery_experience, deye_knowledge, warmth, source, notes, source_date,
                       segment, status, created_at, updated_at
                    ) VALUES (
                       :company_name, :province, :website, :phone, :email, :contact_person, :role,
                       :battery_experience, :deye_knowledge, :warmth, :source, :notes, :source_date,
                       :segment, :status, :created_at, :updated_at
                    )''',
                    {**payload, 'created_at': now},
                )
                inserted += 1

    conn.commit()
    total = conn.execute('SELECT COUNT(*) FROM leads').fetchone()[0]
    conn.close()
    print(f'Inserted: {inserted}')
    print(f'Updated: {updated}')
    print(f'Total leads: {total}')


if __name__ == '__main__':
    main()
