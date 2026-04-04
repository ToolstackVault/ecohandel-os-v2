#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/econtrol-room')
SOURCES_DIR = BASE / 'sources'
STATE_DIR = BASE / 'state'
OUTPUT_PATH = STATE_DIR / 'source-signals.json'
ECODASH_DIR = BASE / 'dashboard-data' / 'data'
ECODASH_FETCH = BASE / 'dashboard-data' / 'scripts' / 'fetch_all.py'

SOURCE_FILES = {
    'manual_topics': SOURCES_DIR / 'manual_topics.json',
    'refresh_candidates': SOURCES_DIR / 'refresh_candidates.json',
    'business_rules': SOURCES_DIR / 'business_rules.json',
    'gsc': ECODASH_DIR / 'gsc.json',
    'shopify': ECODASH_DIR / 'shopify.json',
    'ads': ECODASH_DIR / 'ads.json',
    'ga4': ECODASH_DIR / 'ga4.json',
    'wefact': ECODASH_DIR / 'wefact.json',
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')[:80]


def topic_from_gsc(opportunity: dict, idx: int) -> dict:
    query = opportunity.get('type', '').strip()
    return {
        'id': f'GSC-{idx:03d}',
        'title': query.title(),
        'slug_candidate': slugify(query),
        'content_type': 'money_page' if any(k in query.lower() for k in ['goedkoopste', 'thuisbatterij', 'marstek', 'deye']) else 'support_seo_page',
        'business_goal': 'revenue_direct' if 'thuisbatterij' in query.lower() or 'deye' in query.lower() else 'revenue_support',
        'primary_cluster': 'home_batteries' if 'thuisbatterij' in query.lower() else 'product_specific',
        'secondary_cluster': 'gsc_opportunity',
        'target_audience': 'b2c_homeowner',
        'search_intent': 'commercial_investigational',
        'primary_product_focus': ['home_batteries'] if 'thuisbatterij' in query.lower() else ['product_specific'],
        'supporting_product_focus': [],
        'signal_sources': ['gsc'],
        'why_now': f"GSC opportunity spotted: {opportunity.get('detail', '')}",
        'recommended_format': 'search_capture_page',
        'related_queries': [query],
        'validation_required': True,
        'revenue_potential': 4,
        'seo_potential': 4,
        'commercial_intent': 4,
        'cluster_fit': 4,
        'actuality': 3,
        'authority_value': 2,
        'feasibility': 4,
        'confidence': 0.74,
        'notes': 'Derived from live GSC opportunity snapshot.',
    }


def topic_from_shopify_product(product: dict, idx: int) -> dict:
    name = product.get('name', '').strip()
    focus = 'deye_ecosystem' if 'deye' in name.lower() else 'product_specific'
    return {
        'id': f'SHOP-{idx:03d}',
        'title': f"{name.split('|')[0].strip()}: product focus en use-cases",
        'slug_candidate': slugify(name.split('|')[0].strip()),
        'content_type': 'money_page',
        'business_goal': 'revenue_direct',
        'primary_cluster': focus,
        'secondary_cluster': 'shopify_top_product',
        'target_audience': 'b2c_advanced_buyer',
        'search_intent': 'commercial_solution',
        'primary_product_focus': [focus],
        'supporting_product_focus': ['home_batteries', 'hybrid_inverters'],
        'signal_sources': ['shopify'],
        'why_now': f"Top product from Shopify revenue snapshot: {product.get('detail', '')}",
        'recommended_format': 'solution_guide',
        'related_queries': [name.split('|')[0].strip()],
        'validation_required': True,
        'revenue_potential': 5,
        'seo_potential': 3,
        'commercial_intent': 5,
        'cluster_fit': 4,
        'actuality': 3,
        'authority_value': 3,
        'feasibility': 3,
        'confidence': 0.78,
        'notes': 'Derived from Shopify top-product snapshot.',
    }


def refresh_from_top_page(page: dict, idx: int) -> dict:
    detail = page.get('detail', '')
    severity = 'high' if 'CTR 9,' in detail or 'CTR 10,' in detail else 'medium'
    return {
        'id': f'GSC-RF-{idx:03d}',
        'url': page.get('type', ''),
        'issue_type': 'low_ctr_priority_page',
        'severity': severity,
        'evidence': detail,
        'recommended_fix': 'Review title/meta, product framing and commercial relevance for this high-impression page.',
        'priority': 'P1' if severity == 'high' else 'P2',
        'confidence': 0.76,
    }


def topic_from_ads_campaign(campaign: dict, idx: int) -> dict:
    name = campaign.get('name', '').strip()
    return {
        'id': f'ADS-{idx:03d}',
        'title': f"{name}: landingspagina en value-fit verbeteren",
        'slug_candidate': slugify(name),
        'content_type': 'support_seo_page',
        'business_goal': 'revenue_support',
        'primary_cluster': 'campaign_support',
        'secondary_cluster': 'ads_value_gap',
        'target_audience': 'mixed',
        'search_intent': 'commercial_informational',
        'primary_product_focus': ['deye_ecosystem'] if 'deye' in name.lower() else ['campaign_support'],
        'supporting_product_focus': [],
        'signal_sources': ['ads'],
        'why_now': f"Ads campaign snapshot shows value pressure: {campaign.get('focus', '')}",
        'recommended_format': 'landing_page_support',
        'related_queries': [name],
        'validation_required': False,
        'revenue_potential': 4,
        'seo_potential': 2,
        'commercial_intent': 4,
        'cluster_fit': 3,
        'actuality': 4,
        'authority_value': 1,
        'feasibility': 4,
        'confidence': 0.73,
        'notes': campaign.get('risk', ''),
    }


def maybe_refresh_dashboard_data() -> dict:
    if not ECODASH_FETCH.exists():
        return {'status': 'missing', 'detail': 'Econtrol dashboard-data fetch_all.py not found'}
    try:
        proc = subprocess.run([sys.executable, str(ECODASH_FETCH)], capture_output=True, text=True, timeout=180)
        return {
            'status': 'ok' if proc.returncode == 0 else 'error',
            'returncode': proc.returncode,
            'stdout': (proc.stdout or '').strip()[:500],
            'stderr': (proc.stderr or '').strip()[:500],
        }
    except Exception as exc:
        return {'status': 'error', 'detail': str(exc)}


def main() -> None:
    payload = {
        'updated_at': utc_now(),
        'status': 'ok',
        'sources_loaded': {},
        'topics': [],
        'refresh_candidates': [],
        'business_rules': {},
        'warnings': [],
        'snapshots': {},
    }

    dashboard_data_refresh = maybe_refresh_dashboard_data()
    payload['dashboard_data_refresh'] = dashboard_data_refresh

    manual_topics = load_json(SOURCE_FILES['manual_topics'])
    refresh_candidates = load_json(SOURCE_FILES['refresh_candidates'])
    business_rules = load_json(SOURCE_FILES['business_rules'])
    gsc = load_json(SOURCE_FILES['gsc'])
    shopify = load_json(SOURCE_FILES['shopify'])
    ads = load_json(SOURCE_FILES['ads'])
    ga4 = load_json(SOURCE_FILES['ga4'])
    wefact = load_json(SOURCE_FILES['wefact'])

    topics = list(manual_topics.get('items', []))
    refresh_items = list(refresh_candidates.get('items', []))

    for idx, opp in enumerate(gsc.get('opportunities', []), start=1):
        topics.append(topic_from_gsc(opp, idx))
    for idx, product in enumerate(shopify.get('top_products', []), start=1):
        topics.append(topic_from_shopify_product(product, idx))
    for idx, campaign in enumerate(ads.get('campaigns', []), start=1):
        if campaign.get('status') == 'ENABLED':
            topics.append(topic_from_ads_campaign(campaign, idx))
    for idx, page in enumerate(gsc.get('top_pages', []), start=1):
        detail = page.get('detail', '')
        if 'CTR 9,' in detail or 'CTR 10,' in detail:
            refresh_items.append(refresh_from_top_page(page, idx))

    payload['topics'] = topics
    payload['refresh_candidates'] = refresh_items
    payload['business_rules'] = business_rules
    payload['snapshots'] = {
        'gsc_fetched_at': gsc.get('fetched_at'),
        'shopify_fetched_at': shopify.get('fetched_at'),
        'ads_fetched_at': ads.get('fetched_at'),
        'ga4_fetched_at': ga4.get('fetched_at'),
        'wefact_fetched_at': wefact.get('fetched_at'),
        'ga4_sessions_7d': ga4.get('windows', {}).get('last_7_days', {}).get('sessions'),
        'shopify_revenue_28d': shopify.get('windows', {}).get('last_28_days', {}).get('revenue'),
        'ads_value_28d': ads.get('windows', {}).get('last_28_days', {}).get('conversion_value'),
        'wefact_invoice_total_28d': wefact.get('windows', {}).get('last_28_days', {}).get('invoice_total'),
        'wefact_quotes_28d': wefact.get('windows', {}).get('last_28_days', {}).get('quote_count'),
    }
    payload['sources_loaded'] = {
        'manual_topics': len(manual_topics.get('items', [])),
        'refresh_candidates': len(refresh_candidates.get('items', [])),
        'gsc_opportunities': len(gsc.get('opportunities', [])),
        'shopify_top_products': len(shopify.get('top_products', [])),
        'ads_campaigns': len([c for c in ads.get('campaigns', []) if c.get('status') == 'ENABLED']),
        'wefact_loaded': 1 if wefact else 0,
        'business_rules': 1 if business_rules else 0,
    }

    if not payload['topics']:
        payload['warnings'].append('No topic signals loaded.')
    if not payload['refresh_candidates']:
        payload['warnings'].append('No refresh candidates loaded.')
    if not business_rules:
        payload['warnings'].append('No business rules loaded.')
    if not gsc:
        payload['warnings'].append('GSC snapshot missing.')
    if not shopify:
        payload['warnings'].append('Shopify snapshot missing.')
    if not wefact:
        payload['warnings'].append('Wefact snapshot missing.')
    if dashboard_data_refresh.get('status') != 'ok':
        payload['warnings'].append('Econtrol dashboard-data refresh did not complete cleanly; snapshot fallback used.')

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n')
    print(f'Wrote {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
