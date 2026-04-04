#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/econtrol-room')
QUEUE_PATH = BASE / 'queue' / 'SMART_CONTENT_QUEUE.json'
OUTPUT_PATH = BASE / 'state' / 'specialist-triggers.json'


def load_json(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def main() -> None:
    queue = load_json(QUEUE_PATH)
    triggers = []
    for item in queue.get('top_5_now', []) + queue.get('next_up', []):
        if item.get('validation_required'):
            triggers.append({
                'item_id': item['id'],
                'title': item['title'],
                'trigger_agent': 'fact_product',
                'reason': 'validation_required=true',
            })
        if item.get('business_goal') in {'revenue_direct', 'revenue_support'} and (item.get('confidence') or 0) < 0.8:
            triggers.append({
                'item_id': item['id'],
                'title': item['title'],
                'trigger_agent': 'content_strategist',
                'reason': 'High-value item with moderate confidence',
            })
        if item.get('content_type') == 'authority_page':
            triggers.append({
                'item_id': item['id'],
                'title': item['title'],
                'trigger_agent': 'serp_gap',
                'reason': 'Authority/cluster expansion candidate',
            })

    payload = {
        'updated_at': utc_now(),
        'count': len(triggers),
        'items': triggers,
        'notes': 'Trigger-only specialist suggestions. Nothing auto-runs from this file yet.',
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n')
    print(f'Wrote {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
