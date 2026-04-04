#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/econtrol-room')
STATE_DIR = BASE / 'state'
QUEUE_DIR = BASE / 'queue'

SOURCE_SIGNALS_PATH = STATE_DIR / 'source-signals.json'
SMART_QUEUE_PATH = QUEUE_DIR / 'SMART_CONTENT_QUEUE.json'
REFRESH_QUEUE_PATH = QUEUE_DIR / 'REFRESH_QUEUE.json'
QUEUE_HEALTH_PATH = STATE_DIR / 'queue-health.json'
SOURCE_MIX_PATH = STATE_DIR / 'source-mix.json'
LEARNING_PATH = STATE_DIR / 'learning-summary.json'
CRON_STATUS_PATH = STATE_DIR / 'cron-status.json'
AGENT_STATUS_PATH = STATE_DIR / 'agent-status.json'


def load_json(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def parse_iso(value: str | None):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except Exception:
        return None


def age_hours(value: str | None):
    dt = parse_iso(value)
    if not dt:
        return None
    return round((datetime.now(timezone.utc) - dt).total_seconds() / 3600, 1)


def main() -> None:
    source_signals = load_json(SOURCE_SIGNALS_PATH)
    queue = load_json(SMART_QUEUE_PATH)
    refresh = load_json(REFRESH_QUEUE_PATH)
    agent_status = load_json(AGENT_STATUS_PATH)
    snapshots = source_signals.get('snapshots', {})
    ecodash_refresh = source_signals.get('ecodash_refresh', {})

    all_queue_items = []
    for lane in ['top_5_now', 'next_up', 'refresh_first', 'watchlist', 'killed_noise', 'done']:
        all_queue_items.extend(queue.get(lane, []))

    by_lane = {lane: len(queue.get(lane, [])) for lane in ['top_5_now', 'next_up', 'refresh_first', 'watchlist', 'killed_noise', 'done']}
    by_priority_counter = Counter(item.get('priority_label', 'P5') for item in all_queue_items)
    low_confidence_count = sum(1 for item in all_queue_items if (item.get('confidence') or 0) < 0.65)
    has_refresh_item = any(item.get('content_type') == 'refresh_task' for item in all_queue_items)
    has_p1_item = any(item.get('priority_label') == 'P1' for item in all_queue_items)

    warnings = []
    if by_lane.get('next_up', 0) == 0:
        warnings.append('Next Up lane is empty.')
    if not has_refresh_item:
        warnings.append('No refresh item is active in the queue.')
    if not has_p1_item:
        warnings.append('No P1 item is active in the queue.')
    if len(all_queue_items) < 8:
        warnings.append('Queue depth is still too shallow for healthy autonomy.')
    if (snapshots.get('ads_value_28d') or 0) == 0 and (snapshots.get('shopify_revenue_28d') or 0) > 0:
        warnings.append('Ads value is 0 while Shopify shows revenue: value tracking sanity check needed.')

    freshness = {
        'gsc_age_hours': age_hours(snapshots.get('gsc_fetched_at')),
        'shopify_age_hours': age_hours(snapshots.get('shopify_fetched_at')),
        'ads_age_hours': age_hours(snapshots.get('ads_fetched_at')),
        'ga4_age_hours': age_hours(snapshots.get('ga4_fetched_at')),
    }
    stale_sources = [name for name, hours in freshness.items() if hours is not None and hours > 6]
    if stale_sources:
        warnings.append('Some source snapshots are older than 6 hours: ' + ', '.join(stale_sources))

    queue_health = {
        'updated_at': utc_now(),
        'total_items': len(all_queue_items),
        'by_lane': by_lane,
        'by_priority': {k: by_priority_counter.get(k, 0) for k in ['P1', 'P2', 'P3', 'P4', 'P5']},
        'low_confidence_count': low_confidence_count,
        'stale_count': len(stale_sources),
        'has_refresh_item': has_refresh_item,
        'has_p1_item': has_p1_item,
        'freshness': freshness,
        'warnings': warnings,
    }

    source_counter = Counter()
    for item in all_queue_items:
        for source in item.get('signal_sources', []):
            source_counter[source] += 1
    source_counter['refresh_items'] = len(refresh.get('items', []))

    source_mix = {
        'updated_at': utc_now(),
        'sources': dict(source_counter),
        'notes': 'Generated from deterministic source refresh + queue scoring.',
        'snapshots': snapshots,
    }

    learning_summary = {
        'updated_at': utc_now(),
        'weekly_learning_flags': sum(len(item.get('learning_flags', [])) for item in all_queue_items),
        'recurring_issue_detected': False,
        'notes': 'Deterministic operating system is active; self-improvement aggregation still lightweight.',
    }

    cron_status = {
        'updated_at': utc_now(),
        'ops_cycle_ready': True,
        'source_refresh_ready': SOURCE_SIGNALS_PATH.exists(),
        'queue_scoring_ready': SMART_QUEUE_PATH.exists(),
        'state_update_ready': True,
        'render_ready': (BASE / 'scripts' / 'render_dashboard.py').exists(),
        'queue_page_ready': (BASE / 'scripts' / 'render_queue_page.py').exists(),
        'trigger_logic_ready': (BASE / 'scripts' / 'trigger_specialists.py').exists(),
        'workflow_state_ready': (BASE / 'scripts' / 'generate_workflow_state.py').exists(),
        'workflows_page_ready': (BASE / 'scripts' / 'render_workflows_page.py').exists(),
        'partner_campaign_page_ready': (BASE / 'scripts' / 'render_partner_campaign_page.py').exists(),
        'pwa_assets_ready': (BASE / 'scripts' / 'render_pwa_assets.py').exists(),
        'publish_wrapper_ready': (BASE / 'scripts' / 'publish_ecohandel.py').exists(),
        'publish_system_ready': (BASE / 'sources' / 'publish-system.json').exists() and (Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/content-system/kennisblog/PUBLISH_PLAYBOOK.md')).exists() and (Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/content-system/kennisblog/TEMPLATE.html')).exists() and (Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/content-system/kennisblog/publish_article.py')).exists(),
        'ecodash_live_refresh': ecodash_refresh.get('status') == 'ok',
        'notes': 'Cron status reflects script availability and most recent generated state files.',
    }

    agents = agent_status.get('agents', {})
    if 'ops_agent' in agents:
        agents['ops_agent']['status'] = 'active'
        agents['ops_agent']['last_run'] = utc_now()
        agents['ops_agent']['runs_managed'] = (agents['ops_agent'].get('runs_managed') or 0) + 1
        agents['ops_agent']['notes'] = 'Deterministic ops cycle executed successfully.'
    if 'refresh' in agents:
        agents['refresh']['issues_found'] = len(refresh.get('items', []))
    agent_status['updated_at'] = utc_now()
    agent_status['agents'] = agents

    QUEUE_HEALTH_PATH.write_text(json.dumps(queue_health, indent=2, ensure_ascii=False) + '\n')
    SOURCE_MIX_PATH.write_text(json.dumps(source_mix, indent=2, ensure_ascii=False) + '\n')
    LEARNING_PATH.write_text(json.dumps(learning_summary, indent=2, ensure_ascii=False) + '\n')
    CRON_STATUS_PATH.write_text(json.dumps(cron_status, indent=2, ensure_ascii=False) + '\n')
    AGENT_STATUS_PATH.write_text(json.dumps(agent_status, indent=2, ensure_ascii=False) + '\n')
    print(f'Wrote {QUEUE_HEALTH_PATH}')
    print(f'Wrote {SOURCE_MIX_PATH}')
    print(f'Wrote {LEARNING_PATH}')
    print(f'Wrote {CRON_STATUS_PATH}')
    print(f'Wrote {AGENT_STATUS_PATH}')


if __name__ == '__main__':
    main()
