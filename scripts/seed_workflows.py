#!/usr/bin/env python3
"""Seed the 4 core workflow definitions if they don't exist"""
import sqlite3

DB_PATH = "/var/www/html/control.ecohandel.nl/data/ecohandel.db"
TENANT = "eco001"

WORKFLOWS = [
    {
        "id": "wf-seo-audit",
        "name": "seo_audit",
        "description": "SEO Audit & Content Refresh - daily scan voor verouderde content",
        "driver_type": "cron-daily",
        "owner": "jean",
    },
    {
        "id": "wf-partner-daily",
        "name": "partner_daily_send",
        "description": "Partner Email Campagne A/B - 09:00 + 12:00 daily sends",
        "driver_type": "cron-daily",
        "owner": "jean",
    },
    {
        "id": "wf-daily-briefing",
        "name": "daily_briefing",
        "description": "Ochtend Briefing + Econtrol Room Refresh - cron 07:00",
        "driver_type": "cron",
        "owner": "jean",
    },
    {
        "id": "wf-article-sync",
        "name": "article_sync",
        "description": "Shopify Articles -> OS DB Sync - cron 06:00",
        "driver_type": "cron",
        "owner": "jean",
    },
]

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

for wf in WORKFLOWS:
    cursor.execute("SELECT id FROM workflows WHERE id=?", (wf["id"],))
    if cursor.fetchone():
        print(f"  ⏭️ {wf['name']} already exists ({wf['id']})")
        continue
    cursor.execute(
        """INSERT INTO workflows 
        (id, tenant_id, name, description, driver_type, owner, mode, enabled, approval_required, dependencies, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, 'auto', 1, 0, '[]', datetime('now'), datetime('now'))""",
        (wf["id"], TENANT, wf["name"], wf["description"], wf["driver_type"], wf["owner"])
    )
    print(f"  ✅ Created: {wf['name']} ({wf['id']})")

conn.commit()

# Verify
cursor.execute("SELECT id, name, driver_type, owner, enabled FROM workflows WHERE tenant_id=? ORDER BY id", (TENANT,))
count = 0
for row in cursor.fetchall():
    if row[0].startswith("wf-"):
        print(f"  Core: {row}")
        count += 1

print(f"\n✅ {count} core workflows in DB")
conn.close()
