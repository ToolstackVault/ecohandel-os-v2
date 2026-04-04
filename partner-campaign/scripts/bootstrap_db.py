#!/usr/bin/env python3
from __future__ import annotations

import sqlite3
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/partner-campaign')
DB_PATH = BASE / 'data' / 'partner_campaign.db'
SQL_PATH = BASE / 'DATA_MODEL.sql'


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    sql = SQL_PATH.read_text()
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(sql)
        conn.commit()
    finally:
        conn.close()
    print(f'Bootstrapped database at {DB_PATH}')


if __name__ == '__main__':
    main()
