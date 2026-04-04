#!/usr/bin/env python3
import sqlite3
conn = sqlite3.connect('/var/www/html/control.ecohandel.nl/data/ecohandel.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("Tables:", tables)
for t in tables:
    cur.execute(f"SELECT * FROM {t} LIMIT 3")
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    print(f"\n--- {t} ---")
    print(f"Columns: {cols}")
    print(f"Rows: {len(rows)}")
    for r in rows:
        print(f"  {r}")
conn.close()
