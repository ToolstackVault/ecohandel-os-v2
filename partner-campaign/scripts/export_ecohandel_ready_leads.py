#!/usr/bin/env python3
from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

DB_PATH = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/partner-campaign/data/partner_campaign.db')
OUT_CSV = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/partner-campaign/data/ECOHANDEL_LEADS_READY.csv')
REVIEW_CSV = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/partner-campaign/data/ECOHANDEL_LEADS_REVIEW.csv')

INCLUDE_TERMS = [
    'thuisbatterij', 'installateur', 'deye', 'omvormer', 'zonnepanelen', 'victron',
    'residentieel', 'wallbox', 'laadpaal', 'dealer', 'webshop', 'solar', 'battery'
]
EXCLUDE_TERMS = [
    'netcongestie', 'megabatterij', 'megabatterijen', 'mwh', '100kwh', '5mwh', 'peakshaving',
    'energiehub', 'vakantiepark', 'agrarisch', 'c&i', 'zakelijke batterijen'
]

FIELDS = [
    'company_name', 'email', 'phone', 'website', 'contact_person', 'role', 'warmth',
    'deye_knowledge', 'battery_experience', 'source', 'notes', 'status', 'lead_score', 'hot_score'
]


def classify(row: sqlite3.Row) -> str:
    blob = ' '.join(str(row[k] or '') for k in ['company_name', 'source', 'notes', 'battery_experience', 'deye_knowledge', 'website']).lower()
    include = any(term in blob for term in INCLUDE_TERMS)
    exclude = any(term in blob for term in EXCLUDE_TERMS)
    if include and not exclude:
        return 'ready'
    if exclude and not include:
        return 'exclude'
    return 'review'


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT * FROM leads').fetchall()
    ready, review = [], []
    for row in rows:
        decision = classify(row)
        payload = {field: row[field] for field in FIELDS}
        if decision == 'ready':
            ready.append(payload)
        elif decision == 'review':
            review.append(payload)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(ready)
    with REVIEW_CSV.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(review)
    print(f'Ready leads: {len(ready)} -> {OUT_CSV}')
    print(f'Review leads: {len(review)} -> {REVIEW_CSV}')


if __name__ == '__main__':
    main()
