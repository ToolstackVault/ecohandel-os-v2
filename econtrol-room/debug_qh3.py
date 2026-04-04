#!/usr/bin/env python3
"""Debug queue_health - test with NULL id."""
import sqlite3, json
from datetime import datetime, timezone

DB_PATH = "/var/www/html/control.ecohandel.nl/data/ecohandel.db"
TENANT_ID = "eco001"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')

# Test with NULL id (INTEGER autoincrement)
try:
    cur.execute("INSERT INTO queue_health (id, tenant_id, generated_at, total_items, lane_counts, low_confidence_count, stale_count, health_flags) VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)",
        (TENANT_ID, now, 37, '{"next_up":5}', 6, 0, '[]'))
    conn.commit()
    print("NULL id insert OK - id is autoincrement!")
    conn.rollback()
except Exception as e:
    print(f"NULL id insert failed: {e}")

conn.close()
