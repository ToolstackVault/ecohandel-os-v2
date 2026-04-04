#!/usr/bin/env python3
"""Seed workflows table with 4 new workflow definitions."""
import sqlite3
from datetime import datetime, timezone

DB_PATH = "/var/www/html/control.ecohandel.nl/data/ecohandel.db"
TENANT_ID = "eco001"

workflows = [
    {
        "id": "seo_audit",
        "name": "SEO Audit & Content Refresh",
        "description": "Dagelijkse SEO audit: GSC data refresh, scan op CTR-dalingen, oportunidades identificeren, refresh queue bijwerken.",
        "driver_type": "cron",
        "owner": "ops_agent",
        "mode": "auto",
    },
    {
        "id": "partner_daily_send",
        "name": "Partner Email Campagne A/B",
        "description": "Dagelijkse partner campaign cyclus: stats ophalen, lead scoring, A/B email versturen om 09:00 en 12:00.",
        "driver_type": "cron",
        "owner": "ops_agent",
        "mode": "auto",
    },
    {
        "id": "daily_briefing",
        "name": "Ochtend Briefing + Econtrol Room Refresh",
        "description": "Ochtend briefing voor Milan/Tom: email check, agenda check, belangrijke stats samenvatten, Econtrol Room dashboard verversen.",
        "driver_type": "cron",
        "owner": "ops_agent",
        "mode": "auto",
    },
    {
        "id": "article_sync",
        "name": "Shopify Articles → OS DB Sync",
        "description": "Shopify kennisblog artikelen sync naar EcoHandel OS DB: haalt alle artikelen uit blog 126678466901, update queue_items met nieuwste data.",
        "driver_type": "cron",
        "owner": "ops_agent",
        "mode": "auto",
    },
]

def seed_workflows():
    print(f"[{datetime.now().isoformat()}] Seeding workflows...")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    seeded = 0
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    
    for wf in workflows:
        cur.execute("""
            INSERT OR REPLACE INTO workflows
            (id, tenant_id, name, description, driver_type, owner, mode,
             enabled, approval_required, dependencies, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            wf["id"], TENANT_ID, wf["name"], wf["description"],
            wf["driver_type"], wf["owner"], wf["mode"],
            1, 0, "[]", now, now
        ))
        seeded += 1
        print(f"  Seeded: {wf['id']} - {wf['name']}")
    
    conn.commit()
    
    # Verify via API
    cur.execute("SELECT id, name, driver_type, mode FROM workflows ORDER BY id")
    print("\nAll workflows in DB:")
    for r in cur.fetchall():
        print(f"  [{r['driver_type']}] {r['id']}: {r['name']} ({r['mode']})")
    
    conn.close()
    print(f"\nSeeded {seeded} workflows")
    return seeded

if __name__ == "__main__":
    seed_workflows()
