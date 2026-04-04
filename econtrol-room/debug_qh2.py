#!/usr/bin/env python3
"""Debug queue_health insert - try minimal insert."""
import sqlite3, json
from datetime import datetime, timezone

DB_PATH = "/var/www/html/control.ecohandel.nl/data/ecohandel.db"
TENANT_ID = "eco001"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Check column types
cur.execute("PRAGMA table_info(queue_health)")
cols = cur.fetchall()
for c in cols:
    print(f"  col {c[1]}: type={c[2]}")

# Try inserting one column at a time to find the problem
now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')

# Test with just id, tenant, generated_at
try:
    cur.execute("INSERT INTO queue_health (id, tenant_id, generated_at) VALUES (?, ?, ?)",
        (f"QH-test-{datetime.now().strftime('%H%M%S')}", TENANT_ID, now))
    conn.commit()
    print("Minimal insert OK")
    # Rollback
    conn.rollback()
except Exception as e:
    print(f"Minimal insert failed: {e}")

# Check if tenant_id has UNIQUE or NOT NULL
cur.execute("SELECT COUNT(*) FROM tenants")
tenant_count = cur.fetchone()[0]
print(f"Tenant count: {tenant_count}")

# Check if id is UNIQUE
cur.execute("SELECT id FROM queue_health WHERE tenant_id=?", (TENANT_ID,))
existing = cur.fetchall()
print(f"Existing queue_health records: {len(existing)}")

conn.close()
