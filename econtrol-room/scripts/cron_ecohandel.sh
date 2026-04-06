#!/bin/bash
# cron_ecohandel.sh — Hourly cron: score queue + sync to VPS DB
set -e
BASE="/Users/ecohandel.nl/.openclaw/workspace/ecohandel/econtrol-room"
VPS="root@135.181.148.220"
VPS_ROOT="/var/www/html/control.ecohandel.nl"
QUEUE_JSON="$BASE/queue/SMART_CONTENT_QUEUE.json"
DB="$VPS_ROOT/data/ecohandel.db"
LOG="$BASE/logs/cron_ecohandel.log"

mkdir -p "$BASE/logs"
echo "[$(date '+%Y-%m-%d %H:%M')] === Starting Econtrol Room cycle ===" >> "$LOG"

# Detect python3 (try venvs, fall back to system)
if [ -f "/Users/ecohandel.nl/.openclaw/workspace/.venvs/deye-price-guard/bin/python3" ]; then
    PYTHON3="/Users/ecohandel.nl/.openclaw/workspace/.venvs/deye-price-guard/bin/python3"
elif [ -f "/Users/ecohandel.nl/.openclaw/workspace/.venv/bin/python3" ]; then
    PYTHON3="/Users/ecohandel.nl/.openclaw/workspace/.venv/bin/python3"
else
    PYTHON3="$(command -v python3 2>/dev/null || command -v python 2>/dev/null || echo '/usr/bin/python3')"
fi

if [ -f "/Users/ecohandel.nl/.openclaw/workspace/.venv-googleads311/bin/python3" ]; then
    PYTHON3_GADS="/Users/ecohandel.nl/.openclaw/workspace/.venv-googleads311/bin/python3"
elif [ -f "/Users/ecohandel.nl/.openclaw/workspace/.venv/bin/python3" ]; then
    PYTHON3_GADS="/Users/ecohandel.nl/.openclaw/workspace/.venv/bin/python3"
else
    PYTHON3_GADS="$PYTHON3"
fi

echo "Using PYTHON3=$PYTHON3" >> "$LOG"
echo "Using PYTHON3_GADS=$PYTHON3_GADS" >> "$LOG"

# Step 1: Run score_queue.py locally
echo "[$(date '+%Y-%m-%d %H:%M')] score_queue..." >> "$LOG"
"$PYTHON3" "$BASE/scripts/score_queue.py" >> "$LOG" 2>&1

# Step 1.5: Fetch all dashboard data (GSC, GA4, Ads, Wefact)

echo "[$(date '+%Y-%m-%d %H:%M')] fetch_ads_local..." >> "$LOG"
"$PYTHON3_GADS" "$BASE/dashboard-data/scripts/fetch_ads_local.py" >> "$LOG" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M')] fetch_wefact_local..." >> "$LOG"
"$PYTHON3" "$BASE/scripts/fetch_wefact_local.py" >> "$LOG" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M')] fetch_all dashboard data on VPS..." >> "$LOG"
ssh "$VPS" /opt/ecohandel-venv/bin/python3 /var/www/html/control.ecohandel.nl/dashboard-data/scripts/fetch_all.py >> "$LOG" 2>&1

# Step 1.6: Render all live-facing Econtrol Room pages
for script in \
    "$BASE/scripts/render_dashboard.py" \
    "$BASE/scripts/render_queue_page.py" \
    "$BASE/scripts/generate_workflow_state.py" \
    "$BASE/scripts/render_workflows_page.py" \
    "$BASE/scripts/render_partner_campaign_page.py" \
    "$BASE/scripts/render_pwa_assets.py"
do
    echo "[$(date '+%Y-%m-%d %H:%M')] render $(basename "$script")..." >> "$LOG"
    "$PYTHON3" "$script" >> "$LOG" 2>&1
done

# Step 2: Copy scored JSON, built pages and dashboard data to VPS
echo "[$(date '+%Y-%m-%d %H:%M')] syncing to VPS..." >> "$LOG"
scp -q "$QUEUE_JSON" "$VPS:$VPS_ROOT/data/SMART_CONTENT_QUEUE.json"
rsync -e "ssh -o StrictHostKeyChecking=no" -aq "$BASE/build/" "$VPS:$VPS_ROOT/"
rsync -e "ssh -o StrictHostKeyChecking=no" -aq "$BASE/dashboard-data/data/" "$VPS:$VPS_ROOT/dashboard-data/data/"
ssh "$VPS" "chown -R www-data:www-data '$VPS_ROOT' && find '$VPS_ROOT' -type d -exec chmod 755 {} + && find '$VPS_ROOT' -type f -exec chmod 644 {} + && chmod 640 '$VPS_ROOT/.htpasswd'"

# Step 3: Sync scored items into VPS SQLite DB
ssh "$VPS" /opt/ecohandel-venv/bin/python3 - "$VPS_ROOT/data/SMART_CONTENT_QUEUE.json" "$DB" << 'PYEOF'
import sys, json, sqlite3
from datetime import datetime, timezone

QUEUE_JSON, DB = sys.argv[1], sys.argv[2]
TENANT = 'eco001'

def now_utc():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')

with open(QUEUE_JSON) as f:
    q = json.load(f)

conn = sqlite3.connect(DB)
cur = conn.cursor()
now = now_utc()

lane_data = [
    ('top_5_now', q.get('top_5_now', [])),
    ('next_up', q.get('next_up', [])),
    ('refresh_first', q.get('refresh_first', [])),
    ('watchlist', q.get('watchlist', [])),
    ('killed_noise', q.get('killed_noise', [])),
    ('done', q.get('done', [])),
]

updated = inserted = 0
for lane_key, lane_items in lane_data:
    for item in lane_items:
        item_id = item['id']
        cur.execute('''
            UPDATE queue_items SET lane=?, total_score=?, priority_label=?, confidence=?,
            status=?, why_now=?, recommended_format=?, recommended_next_step=?,
            signal_sources=?, notes=?, refresh_target_url=?, updated_at=?
            WHERE id=? AND tenant_id=?''',
            (lane_key, item.get('total_score', 0), item.get('priority_label','P3'),
             item.get('confidence', 0.5), item.get('status','queued'),
             item.get('why_now',''), item.get('recommended_format',''),
             item.get('recommended_next_step','queue_now'),
             json.dumps(item.get('signal_sources',[])),
             item.get('notes',''), item.get('refresh_target_url'), now,
             item_id, TENANT))
        if cur.rowcount == 0:
            cur.execute('''INSERT INTO queue_items
                (id, tenant_id, title, lane, total_score, priority_label, confidence,
                 status, why_now, recommended_format, recommended_next_step,
                 signal_sources, notes, refresh_target_url, content_type, business_goal,
                 primary_cluster, owner, created_at, updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (item_id, TENANT, item.get('title',''), lane_key,
                 item.get('total_score',0), item.get('priority_label','P3'),
                 item.get('confidence',0.5), item.get('status','queued'),
                 item.get('why_now',''), item.get('recommended_format',''),
                 item.get('recommended_next_step','queue_now'),
                 json.dumps(item.get('signal_sources',[])),
                 item.get('notes',''), item.get('refresh_target_url'),
                 item.get('content_type',''), item.get('business_goal',''),
                 item.get('primary_cluster',''), item.get('owner','jean'), now, now))
            inserted += 1
        updated += 1

conn.commit()
conn.close()
print(f"OK: {updated} updated, {inserted} inserted")
PYEOF

echo "[$(date '+%Y-%m-%d %H:%M')] done" >> "$LOG"
