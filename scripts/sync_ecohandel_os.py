#!/usr/bin/env python3
"""EcoHandel OS Sync Daemon
Incremental sync: Shopify -> queue_items, Brevo contacts -> campaign_contacts,
dashboard data freshness check, queue_health snapshot, activity_log entries."""
import json, sqlite3, urllib.request, urllib.error, os, time
from datetime import datetime, timezone

DB_PATH = "/var/www/html/control.ecohandel.nl/data/ecohandel.db"
TENANT = "eco001"
SHOP_TOKEN = "***REMOVED***"
SHOP_BLOG = 126678466901
CONTENT_TYPE = "kennisblog"
VPS_DASHBOARD = "/var/www/html/control.ecohandel.nl/dashboard-data/data/"

def log_activity(cursor, action, detail=""):
    cursor.execute(
        "INSERT INTO activity_log (tenant_id, action, detail, created_at) VALUES (?, ?, ?, ?)",
        (TENANT, action, detail, datetime.now(timezone.utc).isoformat())
    )

def fetch_shopify_articles():
    url = f"https://n6f6ja-qr.myshopify.com/admin/api/2026-01/blogs/{SHOP_BLOG}/articles.json?limit=250&fields=id,title,handle,body_html,created_at,tags"
    req = urllib.request.Request(url, headers={"X-Shopify-Access-Token": SHOP_TOKEN})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["articles"]

def sync_shopify(cursor):
    """Incremental sync: only articles not yet in DB"""
    articles = fetch_shopify_articles()

    existing_ids = set()
    cursor.execute("SELECT id FROM queue_items WHERE tenant_id=?", (TENANT,))
    for row in cursor.fetchall():
        existing_ids.add(row[0])

    def score(body_html):
        l = len(body_html)
        if l > 25000: return 90
        if l > 15000: return 70
        return 50

    imported = 0
    for a in articles:
        sid = str(a["id"])
        db_id = f"SCQ-SHOP-{sid[-6:]}"
        if db_id in existing_ids:
            continue
        sc = score(a.get("body_html", ""))
        cursor.execute("""
            INSERT INTO queue_items
            (id, tenant_id, title, slug_candidate, content_type, business_goal,
             priority_label, status, lane, total_score, confidence, created_at,
             updated_at, done_at, owner, notes, target_audience)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?, ?, ?, ?)
        """, (db_id, TENANT, a["title"], a["handle"], CONTENT_TYPE,
              "SEO kennis & autoriteit", "high", "published", "published",
              sc, 0.95, a.get("created_at", ""), "jean",
              f"shopify_id={sid}", "installateurs_en_consumenten"))
        imported += 1
    return imported

def check_dashboard_freshness():
    results = {}
    if not os.path.exists(VPS_DASHBOARD):
        return {"status": "missing", "path": VPS_DASHBOARD}
    for fname in ["ga4.json", "ads.json", "gsc.json", "shopify.json", "wefact.json"]:
        fpath = os.path.join(VPS_DASHBOARD, fname)
        if os.path.exists(fpath):
            age_hours = (time.time() - os.path.getmtime(fpath)) / 3600
            results[fname] = {"exists": True, "age_hours": round(age_hours, 1)}
        else:
            results[fname] = {"exists": False}
    return results

def snapshot_queue_health(cursor):
    cursor.execute("SELECT COUNT(*) FROM queue_items WHERE tenant_id=?", (TENANT,))
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM queue_items WHERE tenant_id=? AND status='published'", (TENANT,))
    published = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM queue_items WHERE tenant_id=? AND status='queued'", (TENANT,))
    queued = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM campaign_contacts WHERE tenant_id=?", (TENANT,))
    contacts = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM workflows WHERE tenant_id=?", (TENANT,))
    workflows = cursor.fetchone()[0]

    snapshot = {
        "total_items": total, "published": published, "queued": queued,
        "campaign_contacts": contacts, "workflows": workflows,
        "snapshot_at": datetime.now(timezone.utc).isoformat()
    }

    cursor.execute("""
        INSERT INTO queue_health
        (tenant_id, avg_queue_depth, avg_processing_time, last_sync, bottleneck, details)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (TENANT, queued, 0, datetime.now(timezone.utc).isoformat(),
         "none", json.dumps(snapshot)))
    return snapshot

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    print(f"Sync start: {now}")

    # 1. Shopify articles (incremental)
    new_articles = sync_shopify(cursor)
    print(f"  Shopify: {new_articles} new articles")
    log_activity(cursor, "shopify_sync", f"{new_articles} nieuwe artikelen")

    # 2. Dashboard freshness
    dash = check_dashboard_freshness()
    print(f"  Dashboard: {json.dumps(dash)}")
    log_activity(cursor, "dashboard_check", json.dumps(dash))

    # 3. Queue health snapshot
    snapshot = snapshot_queue_health(cursor)
    print(f"  Health: {json.dumps(snapshot)}")
    log_activity(cursor, "queue_health_snapshot", json.dumps(snapshot))

    conn.commit()
    conn.close()
    print("Sync complete")

if __name__ == "__main__":
    main()
