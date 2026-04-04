#!/usr/bin/env python3
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/partner-campaign')
DB_PATH = BASE / 'data' / 'partner_campaign.db'

POSITIVE = ['interesse', 'bel', 'bellen', 'partner', 'dealer', 'prijs', 'prijslijst', 'meer info', 'afspraak']
NEGATIVE = ['geen interesse', 'stop', 'niet mailen', 'verwijder', 'afmelden']


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def classify(text: str) -> tuple[str, str, str]:
    t = (text or '').lower()
    if any(k in t for k in NEGATIVE):
        return 'negative', 'high', 'UITSLUITEN'
    if any(k in t for k in POSITIVE):
        return 'positive', 'high', 'BEL VANDAAG'
    return 'neutral', 'medium', 'HANDMATIG REVIEWEN'


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM replies WHERE classification = 'unreviewed'").fetchall()
    now = utc_now()
    for row in rows:
        sentiment, urgency, action = classify(row['message_preview'] or '')
        classification = 'interested' if sentiment == 'positive' else 'negative' if sentiment == 'negative' else 'review_needed'
        conn.execute(
            'UPDATE replies SET classification = ?, sentiment = ?, urgency = ?, action_recommendation = ?, updated_at = ? WHERE id = ?',
            (classification, sentiment, urgency, action, now, row['id'])
        )
    conn.commit()
    conn.close()
    print(f'Classified {len(rows)} replies')


if __name__ == '__main__':
    main()
