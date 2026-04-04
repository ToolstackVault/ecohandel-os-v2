#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/econtrol-room')
STATE_DIR = BASE / 'state'
QUEUE_DIR = BASE / 'queue'
SOURCE_SIGNALS_PATH = STATE_DIR / 'source-signals.json'
SMART_QUEUE_PATH = QUEUE_DIR / 'SMART_CONTENT_QUEUE.json'
REFRESH_QUEUE_PATH = QUEUE_DIR / 'REFRESH_QUEUE.json'


def load_json(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def score_topic(item: dict[str, Any], rules: dict[str, Any]) -> dict[str, Any]:
    weights = rules.get('weights', {})
    thresholds = rules.get('thresholds', {})
    score_revenue = int(item.get('revenue_potential', 0) * weights.get('revenue_potential', 5))
    score_seo = int(item.get('seo_potential', 0) * weights.get('seo_potential', 4))
    score_commercial_intent = int(item.get('commercial_intent', 0) * weights.get('commercial_intent', 3))
    score_cluster_fit = int(item.get('cluster_fit', 0) * weights.get('cluster_fit', 3))
    score_actuality = int(item.get('actuality', 0) * weights.get('actuality', 2))
    score_authority = int(item.get('authority_value', 0) * weights.get('authority_value', 2))
    score_feasibility = int(item.get('feasibility', 0) * weights.get('feasibility', 1))

    total_score = min(100, score_revenue + score_seo + score_commercial_intent + score_cluster_fit + score_actuality + score_authority + score_feasibility)

    if total_score >= thresholds.get('p1_score', 82):
        priority = 'P1'
    elif total_score >= thresholds.get('p2_score', 70):
        priority = 'P2'
    elif total_score >= thresholds.get('p3_score', 58):
        priority = 'P3'
    elif total_score >= thresholds.get('p4_score', 45):
        priority = 'P4'
    else:
        priority = 'P5'

    now = utc_now()
    return {
        'id': f"SCQ-{item['id']}",
        'title': item['title'],
        'slug_candidate': item['slug_candidate'],
        'content_type': item['content_type'],
        'business_goal': item['business_goal'],
        'priority_label': priority,
        'status': 'queued',
        'lane': 'watchlist',
        'primary_cluster': item['primary_cluster'],
        'secondary_cluster': item.get('secondary_cluster'),
        'target_audience': item['target_audience'],
        'search_intent': item['search_intent'],
        'primary_product_focus': item.get('primary_product_focus', []),
        'supporting_product_focus': item.get('supporting_product_focus', []),
        'signal_sources': item.get('signal_sources', []),
        'why_now': item['why_now'],
        'recommended_format': item['recommended_format'],
        'recommended_next_step': 'queue_now',
        'owner': 'jean',
        'assigned_agent': None,
        'created_at': now,
        'updated_at': now,
        'confidence': item.get('confidence', 0.7),
        'notes': item.get('notes', ''),
        'related_urls': item.get('related_urls', []),
        'related_queries': item.get('related_queries', []),
        'competitors_seen': item.get('competitors_seen', []),
        'refresh_target_url': None,
        'dependencies': item.get('dependencies', []),
        'validation_required': item.get('validation_required', False),
        'learning_flags': item.get('learning_flags', []),
        'stale_after_days': item.get('stale_after_days', 30),
        'score_revenue': min(25, score_revenue),
        'score_seo': min(20, score_seo),
        'score_commercial_intent': min(15, score_commercial_intent),
        'score_cluster_fit': min(15, score_cluster_fit),
        'score_actuality': min(10, score_actuality),
        'score_authority': min(10, score_authority),
        'score_feasibility': min(5, score_feasibility),
        'penalty_conflict': 0,
        'penalty_evidence': 0,
        'penalty_business_fit': 0,
        'penalty_maintenance': 0,
        'total_score': total_score,
    }


def score_refresh(item: dict[str, Any], rules: dict[str, Any]) -> dict[str, Any]:
    severity = item.get('severity', 'medium')
    bonus = 0
    if severity == 'high':
        bonus = rules.get('refresh', {}).get('high_severity_bonus', 6)
    elif severity == 'medium':
        bonus = rules.get('refresh', {}).get('medium_severity_bonus', 3)
    score = 62 + bonus + int(item.get('confidence', 0.7) * 10)
    return {
        'id': f"RFQ-{item['id']}",
        'url': item['url'],
        'issue_type': item['issue_type'],
        'severity': severity,
        'evidence': item['evidence'],
        'recommended_fix': item['recommended_fix'],
        'priority': item.get('priority', 'P3'),
        'confidence': item.get('confidence', 0.7),
        'updated_at': utc_now(),
        'score': min(100, score),
    }


def main() -> None:
    data = load_json(SOURCE_SIGNALS_PATH)
    rules = data.get('business_rules', {})
    topics = [score_topic(item, rules) for item in data.get('topics', [])]
    refresh = [score_refresh(item, rules) for item in data.get('refresh_candidates', [])]

    priority_rank = {'P1': 5, 'P2': 4, 'P3': 3, 'P4': 2, 'P5': 1}
    goal_rank = {
        'revenue_direct': 5,
        'revenue_support': 4,
        'strategic_positioning': 3,
        'authority': 2,
        'maintenance': 1,
    }
    topics.sort(
        key=lambda x: (
            priority_rank.get(x['priority_label'], 0),
            goal_rank.get(x['business_goal'], 0),
            x['total_score'],
            x['confidence'],
        ),
        reverse=True,
    )
    refresh.sort(key=lambda x: (x['score'], x['confidence']), reverse=True)

    top_count = rules.get('lanes', {}).get('top_5_now', 5)
    next_count = rules.get('lanes', {}).get('next_up', 5)
    watch_count = rules.get('lanes', {}).get('watchlist', 5)

    top = topics[:top_count]
    next_up = topics[top_count:top_count + next_count]
    watchlist = topics[top_count + next_count:top_count + next_count + watch_count]

    if rules.get('refresh', {}).get('force_one_refresh_in_top5', True) and refresh:
        top_refresh = refresh[0]
        refresh_queue_item = {
            'id': f"SCQ-{top_refresh['id']}",
            'title': f"Refresh: {top_refresh['issue_type'].replace('_', ' ')}",
            'slug_candidate': top_refresh['id'].lower(),
            'content_type': 'refresh_task',
            'business_goal': 'maintenance',
            'priority_label': top_refresh['priority'],
            'status': 'refresh_needed',
            'lane': 'top_5_now',
            'primary_cluster': 'refresh',
            'secondary_cluster': None,
            'target_audience': 'mixed',
            'search_intent': 'mixed',
            'primary_product_focus': [],
            'supporting_product_focus': [],
            'signal_sources': ['refresh_scan'],
            'why_now': top_refresh['evidence'],
            'recommended_format': 'refresh_existing_page',
            'recommended_next_step': 'refresh_existing',
            'owner': 'jean',
            'assigned_agent': 'refresh',
            'created_at': utc_now(),
            'updated_at': utc_now(),
            'confidence': top_refresh['confidence'],
            'notes': top_refresh['recommended_fix'],
            'related_urls': [top_refresh['url']],
            'related_queries': [],
            'competitors_seen': [],
            'refresh_target_url': top_refresh['url'],
            'dependencies': [],
            'validation_required': False,
            'learning_flags': [],
            'stale_after_days': 14,
            'score_revenue': 15,
            'score_seo': 15,
            'score_commercial_intent': 8,
            'score_cluster_fit': 8,
            'score_actuality': 8,
            'score_authority': 2,
            'score_feasibility': 5,
            'penalty_conflict': 0,
            'penalty_evidence': 0,
            'penalty_business_fit': 0,
            'penalty_maintenance': 0,
            'total_score': min(100, top_refresh['score']),
        }
        top = [refresh_queue_item] + top[: max(0, top_count - 1)]

    for lane_name, items in [('top_5_now', top), ('next_up', next_up), ('watchlist', watchlist)]:
        for item in items:
            item['lane'] = lane_name

    payload = {
        'generated_at': utc_now(),
        'mode': 'deterministic_revenue_first',
        'top_5_now': top,
        'next_up': next_up,
        'refresh_first': [],
        'watchlist': watchlist,
        'killed_noise': [],
        'done': [],
    }

    refresh_payload = {
        'generated_at': utc_now(),
        'items': refresh,
    }

    SMART_QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SMART_QUEUE_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n')
    REFRESH_QUEUE_PATH.write_text(json.dumps(refresh_payload, indent=2, ensure_ascii=False) + '\n')
    print(f'Wrote {SMART_QUEUE_PATH}')
    print(f'Wrote {REFRESH_QUEUE_PATH}')


if __name__ == '__main__':
    main()
