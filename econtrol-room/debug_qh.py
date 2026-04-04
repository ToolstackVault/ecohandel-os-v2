#!/usr/bin/env python3
"""Debug queue_health insert."""
import sqlite3, json
from datetime import datetime, timezone

DB_PATH = "/var/www/html/control.ecohandel.nl/data/ecohandel.db"
TENANT_ID = "eco001"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
now_ts = datetime.now().strftime('%Y%m%d%H%M%S')

cur.execute("SELECT COUNT(*) FROM queue_items WHERE tenant_id=?", (TENANT_ID,))
total = cur.fetchone()[0]
print(f"total={total} (type={type(total)})")

cur.execute("SELECT COUNT(*) FROM queue_items WHERE tenant_id=? AND priority_label='P1'", (TENANT_ID,))
p1 = cur.fetchone()[0]
print(f"p1={p1} (type={type(p1)})")

cur.execute("SELECT COUNT(*) FROM queue_items WHERE tenant_id=? AND confidence < 0.6", (TENANT_ID,))
low_conf = cur.fetchone()[0]
print(f"low_conf={low_conf} (type={type(low_conf)})")

cur.execute("SELECT lane, COUNT(*) FROM queue_items WHERE tenant_id=? GROUP BY lane", (TENANT_ID,))
lane_rows = cur.fetchall()
lane_counts = {}
for row in lane_rows:
    lane_counts[row[0]] = row[1]
print(f"lane_counts={lane_counts} (type={type(lane_counts)})")

lane_json = json.dumps(lane_counts)
print(f"lane_json={lane_json} (type={type(lane_json)})")

health_flags = '[]'
record_id = f"QH-{now_ts}"

print(f"\nAbout to INSERT:")
print(f"  id={record_id!r} (type={type(record_id)})")
print(f"  tenant_id={TENANT_ID!r}")
print(f"  generated_at={now!r}")
print(f"  total_items={total} (type={type(total)})")
print(f"  p1_count={p1} (type={type(p1)})")
print(f"  lane_counts={lane_json!r}")

try:
    cur.execute("""
        INSERT INTO queue_health
        (id, tenant_id, generated_at, total_items, p1_count, p2_count, p3_count, p4_count, p5_count,
         lane_counts, low_confidence_count, stale_count, health_flags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record_id,
        TENANT_ID,
        now,
        total,
        p1, 0, 0, 0, 0,
        lane_json,
        low_conf,
        0,
        health_flags
    ))
    conn.commit()
    print("INSERT succeeded!")
except Exception as e:
    print(f"INSERT failed: {e}")

conn.close()
