#!/usr/bin/env python3
"""Sync partner leads from CSV into campaign_contacts table"""
import sqlite3, csv

DB_PATH = "/var/www/html/control.ecohandel.nl/data/ecohandel.db"
CSV_PATH = "/var/www/html/control.ecohandel.nl/data/ECOHANDEL_LEADS_READY.csv"
TENANT = "eco001"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

imported = 0
updated = 0
skipped = 0

with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        email = row.get("email", "").strip()
        if not email:
            skipped += 1
            continue

        contact_person = row.get("contact_person", "").strip()
        company_name = row.get("company_name", "").strip()
        warmth = row.get("warmth", "").strip()
        lead_score = row.get("lead_score", "0")
        status = row.get("status", "new").strip()

        first_name = contact_person.split(" ")[0] if contact_person else ""

        try:
            score_val = int(float(lead_score))
        except (ValueError, TypeError):
            score_val = 0

        cursor.execute("SELECT id FROM campaign_contacts WHERE email=? AND tenant_id=?", (email, TENANT))
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                """UPDATE campaign_contacts SET first_name=?, company_name=?, status=?,
                   source=?, engagement_score=?, updated_at=datetime('now')
                   WHERE email=? AND tenant_id=?""",
                (first_name, company_name, status, "csv_import", score_val, email, TENANT)
            )
            updated += 1
        else:
            cursor.execute(
                """INSERT INTO campaign_contacts 
                (tenant_id, email, first_name, company_name, status, source, 
                 engagement_score, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))""",
                (TENANT, email, first_name, company_name, "new", "csv_import", score_val)
            )
            imported += 1

conn.commit()

cursor.execute("SELECT COUNT(*) FROM campaign_contacts WHERE tenant_id=?", (TENANT,))
total = cursor.fetchone()[0]
print(f"Done: {imported} new, {updated} updated, {skipped} skipped (no email)")
print(f"  Total campaign_contacts in DB: {total}")

cursor.execute(
    "SELECT email, first_name, company_name, engagement_score, status FROM campaign_contacts WHERE tenant_id=? ORDER BY engagement_score DESC LIMIT 10",
    (TENANT,)
)
for row in cursor.fetchall():
    print(f"  {row[0]} | {row[1]} | {row[2]} | score={row[3]} | {row[4]}")

conn.close()
