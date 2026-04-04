#!/usr/bin/env python3
"""
EcoHandel OS — Shopify Articles → queue_items Sync
"""
import json, sqlite3, urllib.request, urllib.error, re, os
from datetime import datetime, timezone

SHOPIFY_TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")
SHOPIFY_SHOP = "n6f6ja-qr.myshopify.com"
BLOG_ID = "126678466901"
TENANT_ID = "eco001"
DB_PATH = "/var/www/html/control.ecohandel.nl/data/ecohandel.db"

def shopify_get(endpoint):
    url = f"https://{SHOPIFY_SHOP}/admin/api/2026-01/{endpoint}"
    req = urllib.request.Request(url)
    req.add_header("X-Shopify-Access-Token", SHOPIFY_TOKEN)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"  HTTP error for {endpoint}: {e}")
        return None

def calculate_score(body_html):
    text = re.sub(r'<[^>]+>', '', body_html)
    text_len = len(text)
    if text_len > 25000: return 90
    elif text_len > 15000: return 70
    else: return 50

def make_slug(title):
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    return slug.strip('-')

def sync_articles():
    print(f"[{datetime.now().isoformat()}] Starting Shopify article sync...")
    
    data = shopify_get(f"blogs/{BLOG_ID}/articles.json?limit=50")
    if not data or "articles" not in data:
        print("Failed to fetch articles")
        return 0
    
    articles = data["articles"]
    print(f"Total articles fetched: {len(articles)}")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    synced = 0
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    
    for article in articles:
        article_id = str(article["id"])
        title = article.get("title", "")
        handle = article.get("handle", "")
        body_html = article.get("body_html", "")
        created_at = article.get("created_at", "")
        updated_at = article.get("updated_at", "")
        tags = article.get("tags", "")
        author = article.get("author", "")
        
        slug = handle or make_slug(title)
        score = calculate_score(body_html)
        queue_id = f"SCQ-SHOP-{article_id[-6:]}"
        
        cur.execute("""
            INSERT OR REPLACE INTO queue_items 
            (id, tenant_id, title, slug_candidate, content_type, business_goal,
             status, lane, total_score, confidence, signal_sources, owner,
             priority_label, notes, created_at, updated_at, done_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            queue_id, TENANT_ID, title, slug, "kennisblog", "revenue_support",
            "published", "published", score, score / 100.0,
            '["shopify_sync"]', "jean", "P3",
            f"Shopify article. Author: {author}. Tags: {tags}",
            created_at or now, updated_at or now, created_at or now,
        ))
        synced += 1
    
    conn.commit()
    
    cur.execute("SELECT COUNT(*) FROM queue_items WHERE id LIKE 'SCQ-SHOP-%'")
    db_count = cur.fetchone()[0]
    print(f"Synced: {synced} articles | Verified in DB: {db_count}")
    
    cur.execute("SELECT id, title, total_score, lane FROM queue_items WHERE id LIKE 'SCQ-SHOP-%' ORDER BY total_score DESC")
    for r in cur.fetchall():
        print(f"  [{r['total_score']}] {r['title'][:60]} | {r['id']}")
    
    conn.close()
    return synced

if __name__ == "__main__":
    count = sync_articles()
    print(f"\nDone. {count} articles processed.")
