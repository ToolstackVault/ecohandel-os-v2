#!/usr/bin/env python3
"""
sync_db.py — Sync Econtrol Room JSON state naar SQLite DB.

Dit script leest de bestaande JSON state files en schrijft ze naar SQLite.
Het is de bridge tussen de oude file-based wereld en de nieuwe API.

Run: python3 sync_db.py [--full]
  --full  = drop en herbouw hele DB (bei eerste keer of reset)
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/econtrol-room')
DB_PATH = os.environ.get(
    'ECOHANDEL_DB',
    str(BASE / 'DATABASE' / 'ecohandel.db')
)
SCHEMA_PATH = BASE / 'DATABASE' / 'schema.sql'
SEED_PATH = BASE / 'DATABASE' / 'seed.sql'
TENANT_ID = 'eco001'


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def get_db():
    return sqlite3.connect(DB_PATH)


def init_db(full: bool = False):
    """Initialize database met schema + seed."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    if full:
        print("🔄 Full reset — drop alle tabellen...")
        with open(SCHEMA_PATH) as f:
            conn.executescript(f.read())
        print("✅ Schema loaded")

        print("🌱 Seeding default data...")
        with open(SEED_PATH) as f:
            conn.executescript(f.read())
        print("✅ Seed data loaded")
    else:
        # alleen schema (tabellen already bestaan)
        with open(SCHEMA_PATH) as f:
            conn.executescript(f.read())
    conn.close()
    print(f"✅ Database klaar: {DB_PATH}")


def load_json(path: Path) -> dict | list:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding='utf-8'))


def sync_queue_items(conn: sqlite3.Connection):
    """Sync SMART_CONTENT_QUEUE.json → queue_items table."""
    queue_path = BASE / 'queue' / 'SMART_CONTENT_QUEUE.json'
    data = load_json(queue_path)

    all_items = []
    for lane_key, lane_items in [
        ('top_5_now', data.get('top_5_now', [])),
        ('next_up', data.get('next_up', [])),
        ('refresh_first', data.get('refresh_first', [])),
        ('watchlist', data.get('watchlist', [])),
        ('killed_noise', data.get('killed_noise', [])),
        ('done', data.get('done', data.get('completed', []))),
    ]:
        for item in lane_items:
            item['lane'] = lane_key
            all_items.append(item)

    # Refresh queue items
    refresh_path = BASE / 'queue' / 'REFRESH_QUEUE.json'
    refresh_data = load_json(refresh_path)
    for item in refresh_data.get('items', []):
        item['lane'] = 'refresh_first'
        all_items.append(item)

    if not all_items:
        print("  ⚠️  Geen queue items om te syncen")
        return

    cur = conn.cursor()
    synced = 0
    skipped = 0

    for item in all_items:
        try:
            score = item.get('total_score', 0)
            if isinstance(score, str):
                score = 0

            ss = item.get('signal_sources', [])
            if isinstance(ss, list):
                ss = json.dumps(ss)

            created = item.get('created_at', now_utc())
            updated = item.get('updated_at', created)

            cur.execute(
                """INSERT OR REPLACE INTO queue_items
                   (id, tenant_id, title, slug_candidate, content_type, business_goal,
                    priority_label, status, lane, primary_cluster, secondary_cluster,
                    target_audience, total_score, confidence, signal_sources,
                    why_now, recommended_format, recommended_next_step, owner,
                    assigned_agent, notes, refresh_target_url, created_at, updated_at, done_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    item.get('id', f"SCQ-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{synced+1}"),
                    TENANT_ID,
                    item.get('title', ''),
                    item.get('slug_candidate'),
                    item.get('content_type', 'support_seo'),
                    item.get('business_goal', 'revenue_support'),
                    item.get('priority_label', 'P3'),
                    item.get('status', 'queued'),
                    item.get('lane', 'unqueued'),
                    item.get('primary_cluster'),
                    item.get('secondary_cluster'),
                    item.get('target_audience', 'mixed'),
                    score,
                    item.get('confidence', 0.5),
                    ss,
                    item.get('why_now'),
                    item.get('recommended_format'),
                    item.get('recommended_next_step', 'queue_now'),
                    item.get('owner', 'jean'),
                    item.get('assigned_agent'),
                    item.get('notes'),
                    item.get('refresh_target_url'),
                    created,
                    updated,
                    item.get('done_at'),
                )
            )
            synced += 1
        except Exception as e:
            skipped += 1
            print(f"  ⚠️  Failed item {item.get('id','?')}: {e}")

    conn.commit()
    print(f"  ✅ {synced} queue items gesynced, {skipped} overgeslagen")


def sync_agent_runs(conn: sqlite3.Connection):
    """Sync agent-status.json → agent_runs table."""
    path = BASE / 'state' / 'agent-status.json'
    data = load_json(path)
    if not data or 'agents' not in data:
        print("  ⚠️  Geen agent status om te syncen")
        return

    cur = conn.cursor()
    synced = 0
    for agent_name, info in data.get('agents', {}).items():
        try:
            last_run = info.get('last_run') or now_utc()
            completed = info.get('last_run') or now_utc()
            items_proc = info.get('runs_managed', info.get('items_scored', info.get('items_found', 0)))
            status = info.get('status', 'unknown')
            notes = info.get('notes', '')
            cur.execute(
                """INSERT INTO agent_runs
                   (tenant_id, agent_name, status, started_at, completed_at,
                    items_processed, output_summary)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    TENANT_ID,
                    agent_name,
                    status,
                    last_run,
                    completed,
                    items_proc,
                    notes,
                )
            )
            synced += 1
        except Exception as e:
            print(f"  ⚠️  Failed agent {agent_name}: {e}")

    conn.commit()
    print(f"  ✅ {synced} agent runs gesynced")


def sync_workflow_runs(conn: sqlite3.Connection):
    """Sync workflow-registry.json + workflow-runs.json → workflows + workflow_runs."""
    reg_path = BASE / 'state' / 'workflow-registry.json'
    runs_path = BASE / 'state' / 'workflow-runs.json'
    reg_data = load_json(reg_path)
    runs_data = load_json(runs_path)

    cur = conn.cursor()

    # Sync workflow definitions
    for item in reg_data.get('items', []):
        try:
            cur.execute(
                """INSERT OR IGNORE INTO workflows
                   (id, tenant_id, name, description, driver_type, owner, mode, enabled,
                    approval_required, dependencies, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    item.get('id'),
                    TENANT_ID,
                    item.get('name', ''),
                    item.get('description', ''),
                    item.get('driver_type', 'script'),
                    item.get('owner', 'ops_agent'),
                    item.get('mode', 'auto'),
                    1 if item.get('enabled', True) else 0,
                    1 if item.get('approval_required', False) else 0,
                    json.dumps(item.get('dependencies', [])),
                    item.get('last_run', now_utc()),
                )
            )
        except Exception as e:
            print(f"  ⚠️  Failed workflow {item.get('id')}: {e}")

    # Sync recent runs
    for run in runs_data.get('items', []):
        wf_id = run.get('workflow_id') or run.get('id')
        if not wf_id:
            continue
        try:
            last_run = run.get('last_run') or now_utc()
            cur.execute(
                """INSERT INTO workflow_runs
                   (tenant_id, workflow_id, status, triggered_by, started_at,
                    completed_at, steps_completed, steps_failed, next_actions, health_flags)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    TENANT_ID,
                    wf_id,
                    run.get('status', 'unknown'),
                    run.get('trigger_type', 'cron'),
                    last_run,
                    last_run,
                    0,
                    0,
                    json.dumps([]),
                    json.dumps([]),
                )
            )
        except Exception as e:
            print(f"  ⚠️  Failed workflow run {wf_id}: {e}")

    conn.commit()
    print(f"  ✅ Workflows + runs gesynced")


def sync_campaign_contacts(conn: sqlite3.Connection):
    """Sync partner-campaign-live.json → campaign_contacts table."""
    path = BASE / 'state' / 'partner-campaign-live.json'
    if not path.exists():
        print("  ⚠️  Geen partner campaign data om te syncen")
        return

    data = load_json(path)
    contacts = data.get('contacts', data.get('leads', []))
    if not contacts:
        print("  ⚠️  Geen contacten om te syncen")
        return

    cur = conn.cursor()
    synced = 0
    for c in contacts:
        try:
            cur.execute(
                """INSERT OR IGNORE INTO campaign_contacts
                   (tenant_id, email, first_name, company_name, status, source,
                    brevo_contact_id, engagement_score, open_count, click_count,
                    reply_count, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    TENANT_ID,
                    c.get('email', ''),
                    c.get('first_name'),
                    c.get('company_name'),
                    c.get('status', 'new'),
                    c.get('source', 'manual'),
                    c.get('brevo_contact_id'),
                    c.get('engagement_score', 0),
                    c.get('open_count', 0),
                    c.get('click_count', 0),
                    c.get('reply_count', 0),
                    c.get('created_at', now_utc()),
                    now_utc(),
                )
            )
            synced += 1
        except Exception as e:
            print(f"  ⚠️  Failed contact {c.get('email','?')}: {e}")

    conn.commit()
    print(f"  ✅ {synced} campaign contacts gesynced")


def sync_learning_entries(conn: sqlite3.Connection):
    """Sync learnings van /learn/ folder naar DB."""
    learn_dir = BASE / 'learn'
    if not learn_dir.exists():
        print("  ℹ️  Geen learn folder")
        return

    cur = conn.cursor()
    synced = 0
    for fpath in learn_dir.glob('*.json'):
        try:
            data = json.loads(fpath.read_text())
            entries = data if isinstance(data, list) else [data]
            for entry in entries:
                cur.execute(
                    """INSERT INTO learning_entries
                       (tenant_id, category, title, description, trigger, applied_to, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        TENANT_ID,
                        entry.get('category', 'general'),
                        entry.get('title', fpath.stem),
                        entry.get('description', ''),
                        entry.get('trigger'),
                        entry.get('applied_to'),
                        entry.get('date', now_utc()),
                    )
                )
                synced += 1
        except Exception as e:
            print(f"  ⚠️  Failed learning file {fpath.name}: {e}")

    if synced:
        conn.commit()
        print(f"  ✅ {synced} learning entries gesynced")


def run(full: bool = False):
    print(f"\n🔄 EcoHandel OS — Sync naar SQLite")
    print(f"   DB: {DB_PATH}")
    print(f"   Tenant: {TENANT_ID}")
    print()

    init_db(full=full)

    conn = get_db()
    try:
        print("📋 Syncing queue items...")
        sync_queue_items(conn)
        print("🤖 Syncing agent runs...")
        sync_agent_runs(conn)
        print("⚙️  Syncing workflows...")
        sync_workflow_runs(conn)
        print("📧 Syncing campaign contacts...")
        sync_campaign_contacts(conn)
        print("📚 Syncing learnings...")
        sync_learning_entries(conn)
    finally:
        conn.close()

    print("\n✅ Sync complete!")
    print(f"   DB: {DB_PATH}")
    print("   Nu: API starten met  python3 API/app.py")


if __name__ == '__main__':
    full = '--full' in sys.argv or '--reset' in sys.argv
    run(full=full)
