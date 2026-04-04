#!/usr/bin/env python3
"""
sync_queue_to_db.py — Sync SMART_CONTENT_QUEUE.json → SQLite queue_items table.

Reads queue/SMART_CONTENT_QUEUE.json, upserts each item into the VPS SQLite DB.
Bridge: file-based scoring output → live Flask API.

Usage:
    python3 scripts/sync_queue_to_db.py
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/econtrol-room')
QUEUE_JSON = BASE / 'queue' / 'SMART_CONTENT_QUEUE.json'

# VPS SQLite DB (same path as Flask API uses)
VPS_DB = os.environ.get(
    'ECOHANDEL_DB',
    '/var/www/html/control.ecohandel.nl/data/ecohandel.db'
)

TENANT_ID = 'eco001'


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def get_conn():
    return sqlite3.connect(VPS_DB)


def sync_queue_items(items: list[dict]) -> dict:
    """Upsert queue items from scored JSON into SQLite."""
    synced = 0
    skipped = 0
    errors = []

    conn = get_conn()
    cur = conn.cursor()

    # Build lane → lane_key mapping from the JSON
    lane_map = {
        'top_5_now': 'top_5_now',
        'next_up': 'next_up',
        'refresh_first': 'refresh_first',
        'watchlist': 'watchlist',
        'killed_noise': 'killed_noise',
        'done': 'done',
    }

    for item in items:
        lane = item.get('lane', 'unqueued')
        if lane not in lane_map:
            lane = 'unqueued'

        # Normalise score fields
        score = item.get('total_score', 0)
        confidence = item.get('confidence', 0.5)
        signal_sources = json.dumps(item.get('signal_sources', []))
        related_queries = json.dumps(item.get('related_queries', []))
        related_urls = json.dumps(item.get('related_urls', []))
        refresh_target_url = item.get('refresh_target_url') or None
        done_at = item.get('done_at') or None

        try:
            cur.execute("""
                INSERT OR REPLACE INTO queue_items (
                    id, tenant_id, title, slug_candidate, content_type,
                    business_goal, priority_label, status, lane,
                    primary_cluster, secondary_cluster, target_audience,
                    total_score, confidence,
                    signal_sources, why_now, recommended_format,
                    recommended_next_step, owner, assigned_agent, notes,
                    refresh_target_url,
                    created_at, updated_at, done_at
                ) VALUES (
                    :id, :tenant_id, :title, :slug_candidate, :content_type,
                    :business_goal, :priority_label, :status, :lane,
                    :primary_cluster, :secondary_cluster, :target_audience,
                    :total_score, :confidence,
                    :signal_sources, :why_now, :recommended_format,
                    :recommended_next_step, :owner, :assigned_agent, :notes,
                    :refresh_target_url,
                    :created_at, :updated_at, :done_at
                )
            """, {
                'id': item.get('id'),
                'tenant_id': TENANT_ID,
                'title': item.get('title', 'Untitled'),
                'slug_candidate': item.get('slug_candidate'),
                'content_type': item.get('content_type', 'article'),
                'business_goal': item.get('business_goal', 'unknown'),
                'priority_label': item.get('priority_label', 'P3'),
                'status': item.get('status', 'new'),
                'lane': lane,
                'primary_cluster': item.get('primary_cluster'),
                'secondary_cluster': item.get('secondary_cluster'),
                'target_audience': item.get('target_audience', 'mixed'),
                'total_score': score,
                'confidence': confidence,
                'signal_sources': signal_sources,
                'why_now': item.get('why_now'),
                'recommended_format': item.get('recommended_format'),
                'recommended_next_step': item.get('recommended_next_step'),
                'owner': item.get('owner', 'jean'),
                'assigned_agent': item.get('assigned_agent'),
                'notes': item.get('notes'),
                'refresh_target_url': refresh_target_url,
                'created_at': item.get('created_at', now_utc()),
                'updated_at': item.get('updated_at', now_utc()),
                'done_at': done_at,
            })
            synced += 1
        except Exception as e:
            errors.append(f"{item.get('id', '?')}: {e}")
            skipped += 1

    conn.commit()
    conn.close()
    return {'synced': synced, 'skipped': skipped, 'errors': errors}


def sync_queue_health(generated_at: str, items_by_lane: dict) -> dict:
    """Update queue_health snapshot."""
    total = sum(items_by_lane.values())
    health_score = min(100, int((total / 20) * 100)) if total > 0 else 50

    conn = get_conn()
    cur = conn.cursor()

    # Count P-levels from top_5_now + next_up items
    p1 = items_by_lane.get('top_5_now', 0)
    p2 = items_by_lane.get('next_up', 0)
    p3 = items_by_lane.get('refresh_first', 0)
    p4 = items_by_lane.get('watchlist', 0)
    p5 = items_by_lane.get('killed_noise', 0)

    import json as _json
    lane_counts = _json.dumps(items_by_lane)

    cur.execute("""
        INSERT INTO queue_health (
            tenant_id, generated_at, total_items,
            p1_count, p2_count, p3_count, p4_count, p5_count,
            lane_counts, low_confidence_count, stale_count, health_flags
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        TENANT_ID, generated_at, total,
        p1, p2, p3, p4, p5,
        lane_counts, 0, 0, '[]'
    ))
    conn.commit()
    conn.close()
    return {'health_score': health_score, 'total': total}


def main():
    print(f"[sync_queue_to_db] Reading {QUEUE_JSON}")
    if not QUEUE_JSON.exists():
        print(f"[sync_queue_to_db] ERROR: {QUEUE_JSON} not found!")
        sys.exit(1)

    data = json.loads(QUEUE_JSON.read_text())
    generated_at = data.get('generated_at', now_utc())

    # Collect all items from all lane keys
    lane_keys = ['top_5_now', 'next_up', 'refresh_first', 'watchlist', 'killed_noise', 'done']
    all_items = []
    items_by_lane = {}

    for lane_key in lane_keys:
        lane_items = data.get(lane_key, [])
        items_by_lane[lane_key] = len(lane_items)
        for item in lane_items:
            item['lane'] = lane_key  # ensure lane is set
            all_items.append(item)

    print(f"[sync_queue_to_db] Total items to sync: {len(all_items)}")
    for lane, cnt in items_by_lane.items():
        if cnt > 0:
            print(f"  {lane}: {cnt}")

    # Sync queue items
    result = sync_queue_items(all_items)
    print(f"[sync_queue_to_db] Synced: {result['synced']}, Skipped: {result['skipped']}")
    if result['errors']:
        for e in result['errors'][:5]:
            print(f"  ERROR: {e}")

    # Sync health snapshot
    health_result = sync_queue_health(generated_at, items_by_lane)
    print(f"[sync_queue_to_db] Health: score={health_result['health_score']}, total={health_result['total']}")

    # Also push an ops_log entry
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO ops_log (tenant_id, action, details, created_at)
            VALUES (?, ?, ?, ?)
        """, (TENANT_ID, 'queue_sync', json.dumps({
            'items_synced': result['synced'],
            'generated_at': generated_at,
            'lanes': items_by_lane,
        }), now_utc()))
        conn.commit()
        conn.close()
        print("[sync_queue_to_db] ops_log entry written")
    except Exception as e:
        print(f"[sync_queue_to_db] ops_log write failed (table may not exist): {e}")

    print("[sync_queue_to_db] Done.")


if __name__ == '__main__':
    main()
