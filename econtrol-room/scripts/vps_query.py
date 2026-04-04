#!/usr/bin/env python3
import sqlite3, json
conn = sqlite3.connect('/var/www/html/control.ecohandel.nl/data/ecohandel.db')
cur = conn.cursor()

# List tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("Tables:", tables)

# Sample queue_items
cur.execute("SELECT id, title, lane, status, total_score, priority_label FROM queue_items LIMIT 10")
rows = cur.fetchall()
print("\nQueue items sample:")
for r in rows:
    print(f"  {r}")

# Workflow tables
for t in tables:
    if 'workflow' in t.lower():
        cur.execute(f"SELECT * FROM {t} LIMIT 3")
        rows = cur.fetchall()
        print(f"\n{t}: {len(rows)} rows (sample)")
        for r in rows:
            print(f"  {r}")
