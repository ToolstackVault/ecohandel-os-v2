#!/usr/bin/env python3
"""Fetch live Brevo campaign stats + local DB stats and write partner-campaign state JSON.

Model-agnostic: any agent/model can run this script to refresh partner data.
Output: ecohandel/econtrol-room/state/partner-campaign-live.json
"""
from __future__ import annotations

import json
import os
import sqlite3
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

# === Paths ===
PARTNER_BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/partner-campaign')
CONFIG_PATH = PARTNER_BASE / 'config.local.json'
APIS_ENV_PATH = Path('/Users/ecohandel.nl/.openclaw/workspace/.env/apis.env')
DB_PATH = PARTNER_BASE / 'data' / 'partner_campaign.db'
STATE_DIR = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/econtrol-room/state')
OUTPUT_PATH = STATE_DIR / 'partner-campaign-live.json'


BAD_EMAIL_TOKENS = (
    'test@',
    'example.com',
    '{{contact.',
)

BAD_EMAIL_SUFFIXES = (
    '@ecohandel.nl',
    '@nova-cell.com',
    '@dekeizonnepanelen.nl',
)

BAD_TEXT_TOKENS = (
    'test',
    'example',
    'jean test',
    'jean cta',
    'webhook test',
    'partner-button-check',
    '__campaign_key__',
    'nova-cell',
    'de kei',
    'bekend contact',
)

BAD_TAG_TOKENS = (
    'brevo-test',
    'partner-webhook-test',
    'tom-send',
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def norm(value: object) -> str:
    return str(value or '').strip().lower()


def is_internal_or_test_email(email: object) -> bool:
    e = norm(email)
    if not e:
        return False
    if any(token in e for token in BAD_EMAIL_TOKENS):
        return True
    if any(e.endswith(suffix) for suffix in BAD_EMAIL_SUFFIXES):
        return True
    return False


def text_has_bad_token(*parts: object) -> bool:
    blob = ' '.join(norm(p) for p in parts if p)
    return any(token in blob for token in BAD_TEXT_TOKENS)


def is_real_db_lead_row(row: sqlite3.Row | dict | None) -> bool:
    if not row:
        return False
    email = row['email'] if isinstance(row, sqlite3.Row) else row.get('email')
    company_name = row['company_name'] if isinstance(row, sqlite3.Row) else row.get('company_name')
    contact_person = row['contact_person'] if isinstance(row, sqlite3.Row) else row.get('contact_person')
    if is_internal_or_test_email(email):
        return False
    if text_has_bad_token(company_name, contact_person):
        return False
    return True


def is_real_brevo_campaign(campaign: dict) -> bool:
    return not text_has_bad_token(
        campaign.get('name'),
        campaign.get('subject'),
        campaign.get('tag'),
    ) and not any(token in norm(campaign.get('tag')) for token in BAD_TAG_TOKENS)


def is_real_transactional_event(event: dict) -> bool:
    return not is_internal_or_test_email(event.get('email')) and not text_has_bad_token(
        event.get('subject'),
        event.get('tag'),
    ) and not any(token in norm(event.get('tag')) for token in BAD_TAG_TOKENS)


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding='utf-8'))


def load_env_file(path: Path) -> dict:
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def choose_brevo_key(cfg: dict) -> tuple[str, str]:
    env = load_env_file(APIS_ENV_PATH)
    candidates = [
        ('config.brevo.api_key', cfg.get('brevo', {}).get('api_key') or ''),
        ('env.BREVO_ECOHANDEL_API_KEY', env.get('BREVO_ECOHANDEL_API_KEY') or os.environ.get('BREVO_ECOHANDEL_API_KEY') or ''),
        ('env.BREVO_API_KEY', env.get('BREVO_API_KEY') or os.environ.get('BREVO_API_KEY') or ''),
    ]
    seen: set[str] = set()
    for source, key in candidates:
        if not key or key in seen:
            continue
        seen.add(key)
        status, payload = brevo_get(key, '/account')
        if status < 400 and isinstance(payload, dict) and payload.get('email'):
            return key, source
    return cfg.get('brevo', {}).get('api_key') or '', 'config.brevo.api_key'


def brevo_get(api_key: str, path: str, query: dict | None = None) -> tuple[int, dict]:
    url = 'https://api.brevo.com/v3' + path
    if query:
        url += '?' + urllib.parse.urlencode(query)
    req = urllib.request.Request(url, headers={
        'accept': 'application/json',
        'api-key': api_key,
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode('utf-8')
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {'raw': body}
    except Exception as exc:
        return 0, {'error': str(exc)}


def fetch_brevo_data(api_key: str, key_source: str) -> dict:
    """Fetch account, senders, lists, campaigns and transactional activity from Brevo."""
    data: dict = {'fetched_at': utc_now(), 'brevo_ok': False, 'api_key_source': key_source}

    # Account
    status, account = brevo_get(api_key, '/account')
    if status >= 400:
        detail = account.get('message') or account.get('error') or account.get('raw') or 'unknown error'
        data['error'] = f'Account fetch failed ({status}): {detail}'
        return data
    data['brevo_ok'] = True
    data['account_email'] = account.get('email', '')
    data['company'] = account.get('companyName', '')
    plan = account.get('plan', [])
    if isinstance(plan, list) and plan:
        data['plan'] = plan[0].get('type', 'unknown')
        data['credits_remaining'] = plan[0].get('credits', 0)
    else:
        data['plan'] = 'unknown'
        data['credits_remaining'] = 0

    # Senders
    _, senders_resp = brevo_get(api_key, '/senders')
    senders = senders_resp.get('senders', []) if isinstance(senders_resp, dict) else []
    data['senders'] = [{'name': s.get('name'), 'email': s.get('email'), 'active': s.get('active')} for s in senders]
    sender_email = str(load_config().get('brevo', {}).get('sender_email') or '').strip().lower()
    sender_match = next((s for s in data['senders'] if str(s.get('email') or '').strip().lower() == sender_email), None)
    data['configured_sender'] = {
        'email': sender_email,
        'active': bool(sender_match.get('active')) if sender_match else False,
        'found': bool(sender_match),
    }

    # Lists
    _, lists_resp = brevo_get(api_key, '/contacts/lists', query={'limit': 50, 'offset': 0})
    lists_data = lists_resp.get('lists', []) if isinstance(lists_resp, dict) else []
    data['lists'] = []
    for lst in lists_data:
        data['lists'].append({
            'id': lst.get('id'),
            'name': lst.get('name'),
            'totalSubscribers': lst.get('totalSubscribers', 0),
            'totalBlacklisted': lst.get('totalBlacklisted', 0),
        })
    data['total_subscribers'] = sum(l.get('totalSubscribers', 0) for l in data['lists'])

    # Campaigns (last 20)
    _, camp_resp = brevo_get(api_key, '/emailCampaigns', query={'limit': 20, 'offset': 0, 'sort': 'desc'})
    campaigns = camp_resp.get('campaigns', []) if isinstance(camp_resp, dict) else []
    data['campaigns'] = []
    for c in campaigns:
        stats = c.get('statistics', {}).get('globalStats', {}) or {}
        item = {
            'id': c.get('id'),
            'name': c.get('name', ''),
            'subject': c.get('subject', ''),
            'status': c.get('status', ''),
            'tag': c.get('tag', ''),
            'sentDate': c.get('sentDate', ''),
            'stats': {
                'sent': stats.get('sent', 0),
                'delivered': stats.get('delivered', 0),
                'opens': stats.get('uniqueOpens', 0),
                'clicks': stats.get('uniqueClicks', 0),
                'unsubscriptions': stats.get('unsubscriptions', 0),
                'hardBounces': stats.get('hardBounces', 0),
                'softBounces': stats.get('softBounces', 0),
            },
        }
        if is_real_brevo_campaign(item):
            data['campaigns'].append(item)

    # Transactional events (this is the real source for our current send flow)
    start_date = (datetime.now(timezone.utc).date() - timedelta(days=7)).isoformat()
    end_date = datetime.now(timezone.utc).date().isoformat()
    _, smtp_events_resp = brevo_get(api_key, '/smtp/statistics/events', query={
        'limit': 500,
        'offset': 0,
        'startDate': start_date,
        'endDate': end_date,
    })
    smtp_events = smtp_events_resp.get('events', []) if isinstance(smtp_events_resp, dict) else []
    data['transactional_events'] = [event for event in smtp_events if is_real_transactional_event(event)]

    transactional_by_tag: dict[str, dict] = {}
    for event in data['transactional_events']:
        tag = str(event.get('tag') or 'untagged')
        subject = str(event.get('subject') or '')
        email = str(event.get('email') or '')
        bucket = transactional_by_tag.setdefault(tag, {
            'tag': tag,
            'subjects': set(),
            'recipients': set(),
            'delivered': 0,
            'opened': 0,
            'clicks': 0,
            'requests': 0,
            'hard_bounce': 0,
            'soft_bounce': 0,
            'unsubscribe': 0,
            'error': 0,
            'errors': [],
            'delivered_recipients': set(),
            'opened_recipients': set(),
            'clicked_recipients': set(),
            'unsubscribed_recipients': set(),
            'bounced_recipients': set(),
        })
        if subject:
            bucket['subjects'].add(subject)
        if email:
            bucket['recipients'].add(email.lower())
        ev = str(event.get('event') or '').lower()
        if ev in bucket:
            bucket[ev] += 1
        if email:
            if ev == 'delivered':
                bucket['delivered_recipients'].add(email.lower())
            elif ev == 'opened':
                bucket['opened_recipients'].add(email.lower())
            elif ev == 'clicked':
                bucket['clicked_recipients'].add(email.lower())
            elif ev == 'unsubscribe':
                bucket['unsubscribed_recipients'].add(email.lower())
            elif ev in {'hard_bounce', 'soft_bounce'}:
                bucket['bounced_recipients'].add(email.lower())
        if ev == 'error' and event.get('reason'):
            bucket['errors'].append(str(event.get('reason')))

    data['transactional_summary'] = []
    for tag, bucket in transactional_by_tag.items():
        data['transactional_summary'].append({
            'tag': tag,
            'subjects': sorted(bucket['subjects']),
            'unique_recipients': len(bucket['recipients']),
            'recipient_samples': sorted(list(bucket['recipients']))[:10],
            'delivered': bucket['delivered'],
            'opened': bucket['opened'],
            'clicks': bucket['clicks'],
            'requests': bucket['requests'],
            'hard_bounce': bucket['hard_bounce'],
            'soft_bounce': bucket['soft_bounce'],
            'unsubscribe': bucket['unsubscribe'],
            'error': bucket['error'],
            'unique_delivered': len(bucket['delivered_recipients']),
            'unique_opened': len(bucket['opened_recipients']),
            'unique_clicked': len(bucket['clicked_recipients']),
            'unique_unsubscribed': len(bucket['unsubscribed_recipients']),
            'unique_bounced': len(bucket['bounced_recipients']),
            'errors': bucket['errors'][:5],
        })

    # Aggregate campaign KPIs (campaign API)
    total_sent = sum(c['stats']['sent'] for c in data['campaigns'])
    total_delivered = sum(c['stats']['delivered'] for c in data['campaigns'])
    total_opens = sum(c['stats']['opens'] for c in data['campaigns'])
    total_clicks = sum(c['stats']['clicks'] for c in data['campaigns'])
    total_unsubs = sum(c['stats']['unsubscriptions'] for c in data['campaigns'])
    total_hard_bounces = sum(c['stats']['hardBounces'] for c in data['campaigns'])

    # Aggregate transactional KPIs (actual current send path)
    tx_delivered = sum(item['unique_delivered'] for item in data['transactional_summary'])
    tx_opened = sum(item['unique_opened'] for item in data['transactional_summary'])
    tx_clicks = sum(item['unique_clicked'] for item in data['transactional_summary'])
    tx_unsubs = sum(item['unique_unsubscribed'] for item in data['transactional_summary'])
    tx_bounces = sum(item['unique_bounced'] for item in data['transactional_summary'])
    tx_errors = sum(item['error'] for item in data['transactional_summary'])
    tx_unique_recipients = sum(item['unique_recipients'] for item in data['transactional_summary'])

    data['kpi'] = {
        'total_campaigns': len(data['campaigns']),
        'total_sent': total_sent,
        'total_delivered': total_delivered,
        'total_opens': total_opens,
        'total_clicks': total_clicks,
        'total_unsubs': total_unsubs,
        'total_hard_bounces': total_hard_bounces,
        'open_rate': round(total_opens / total_delivered * 100, 1) if total_delivered else 0,
        'click_rate': round(total_clicks / total_delivered * 100, 1) if total_delivered else 0,
        'unsub_rate': round(total_unsubs / total_delivered * 100, 1) if total_delivered else 0,
        'bounce_rate': round(total_hard_bounces / total_sent * 100, 1) if total_sent else 0,
    }
    data['transactional_kpi'] = {
        'unique_recipients': tx_unique_recipients,
        'delivered': tx_delivered,
        'opened': tx_opened,
        'clicks': tx_clicks,
        'unsubs': tx_unsubs,
        'hard_bounces': tx_bounces,
        'errors': tx_errors,
        'open_rate': round(tx_opened / tx_delivered * 100, 1) if tx_delivered else 0,
        'click_rate': round(tx_clicks / tx_delivered * 100, 1) if tx_delivered else 0,
        'unsub_rate': round(tx_unsubs / tx_delivered * 100, 1) if tx_delivered else 0,
        'bounce_rate': round(tx_bounces / tx_unique_recipients * 100, 1) if tx_unique_recipients else 0,
    }

    return data


def fetch_db_stats() -> dict:
    """Read local SQLite DB for lead stats, hot prospects, status distribution."""
    data: dict = {'db_ok': False}

    if not DB_PATH.exists():
        data['error'] = f'DB not found: {DB_PATH}'
        return data

    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        data['db_ok'] = True

        all_leads = [dict(r) for r in conn.execute('SELECT * FROM leads').fetchall()]
        real_leads = [row for row in all_leads if is_real_db_lead_row(row)]

        data['total_leads_raw'] = len(all_leads)
        data['total_leads'] = len(real_leads)
        data['leads_with_email'] = sum(1 for row in real_leads if norm(row.get('email')))
        data['contactable'] = sum(
            1 for row in real_leads
            if not row.get('do_not_contact') and not row.get('unsubscribed') and not row.get('bounced')
        )

        status_distribution: dict[str, int] = {}
        warmth_distribution: dict[str, int] = {}
        for row in real_leads:
            status = str(row.get('status') or 'unknown')
            status_distribution[status] = status_distribution.get(status, 0) + 1
            warmth = str(row.get('warmth') or '').strip()
            if warmth:
                warmth_distribution[warmth] = warmth_distribution.get(warmth, 0) + 1
        data['status_distribution'] = dict(sorted(status_distribution.items(), key=lambda x: -x[1]))
        data['warmth_distribution'] = dict(sorted(warmth_distribution.items(), key=lambda x: -x[1]))

        # Hot prospects: engagement (hot_score) first, fit (lead_score) as tiebreaker
        cur.execute('''
            SELECT company_name, contact_person, email, warmth, status,
                   lead_score, hot_score, (lead_score + hot_score) as total_score,
                   last_activity_at
            FROM leads
            WHERE do_not_contact = 0
              AND unsubscribed = 0
              AND bounced = 0
              AND email IS NOT NULL
              AND email != ''
              AND email NOT LIKE '%{{%'
              AND lower(email) NOT LIKE '%@ecohandel.nl'
              AND lower(email) NOT LIKE '%@nova-cell.com'
              AND lower(email) NOT LIKE '%@dekeizonnepanelen.nl'
              AND lower(email) NOT LIKE '%@outlook.com'
              AND lower(email) NOT LIKE '%@hotmail.com'
              AND lower(email) NOT LIKE '%@gmail.com'
              AND lower(company_name) NOT LIKE '%milan%'
              AND lower(company_name) NOT LIKE '%bekend contact%'
              AND lower(company_name) NOT LIKE '%ecohandel%'
              AND lower(company_name) NOT LIKE '%nova-cell%'
              AND lower(company_name) NOT LIKE '%de kei%'
            ORDER BY hot_score DESC, lead_score DESC
            LIMIT 25
        ''')
        data['hot_prospects'] = []
        for row in cur.fetchall():
            data['hot_prospects'].append(dict(row))

        # Engagement summary from lead_campaigns
        try:
            real_lead_ids = [int(row['id']) for row in real_leads]
            if real_lead_ids:
                placeholders = ','.join('?' for _ in real_lead_ids)
                cur.execute(f'''
                    SELECT
                        SUM(open_count) as total_opens,
                        SUM(click_count) as total_clicks,
                        SUM(reply_count) as total_replies,
                        SUM(unsubscribe_count) as total_unsubs,
                        SUM(bounce_count) as total_bounces,
                        COUNT(DISTINCT lead_id) as leads_reached
                    FROM lead_campaigns
                    WHERE lead_id IN ({placeholders})
                ''', real_lead_ids)
                row = cur.fetchone()
                data['engagement'] = dict(row) if row and row['leads_reached'] else {}
                data['used_real_leads'] = int(row['leads_reached'] or 0) if row else 0
            else:
                data['engagement'] = {}
                data['used_real_leads'] = 0
        except Exception:
            data['engagement'] = {}
            data['used_real_leads'] = 0

        # Recent events (last 50)
        try:
            cur.execute('''
                SELECT event_type, email, event_ts
                FROM events
                ORDER BY event_ts DESC
                LIMIT 200
            ''')
            data['recent_events'] = [dict(r) for r in cur.fetchall() if not is_internal_or_test_email(r['email'])][:50]
        except Exception:
            data['recent_events'] = []

        # Campaign records from local DB
        try:
            cur.execute('''
                SELECT id, name, campaign_type, subject_line, status, created_at
                FROM campaigns
                ORDER BY created_at DESC
                LIMIT 50
            ''')
            data['local_campaigns'] = [dict(r) for r in cur.fetchall() if not text_has_bad_token(r['name'], r['subject_line'])][:10]
        except Exception:
            data['local_campaigns'] = []

        # Daily reports (last 7)
        try:
            cur.execute('''
                SELECT report_date, hot_count, replied_count, opened_count,
                       clicked_count, unsubscribed_count, bounced_count
                FROM daily_reports
                ORDER BY report_date DESC
                LIMIT 7
            ''')
            data['daily_reports'] = [dict(r) for r in cur.fetchall()]
        except Exception:
            data['daily_reports'] = []

        conn.close()
    except Exception as exc:
        data['error'] = str(exc)

    return data


def compute_recommendations(brevo: dict, db: dict) -> list[dict]:
    """Generate actionable recommendations based on live data."""
    recs: list[dict] = []

    # Check if campaigns have been sent
    kpi = brevo.get('kpi', {})
    tx = brevo.get('transactional_kpi', {})

    configured_sender = brevo.get('configured_sender') or {}
    if brevo.get('brevo_ok') and (not configured_sender.get('found') or not configured_sender.get('active')):
        recs.append({
            'priority': 'high',
            'type': 'blocker',
            'title': 'Brevo sender info@ecohandel.nl is niet actief',
            'detail': 'Nieuwe sends kunnen worden geweigerd totdat de sender/domeinverificatie in Brevo weer actief is.',
        })

    if tx.get('errors', 0) > 0:
        recs.append({
            'priority': 'high',
            'type': 'blocker',
            'title': f'Brevo registreert {tx.get("errors", 0)} send errors',
            'detail': 'Dit is geen tracking-issue maar een deliverability/sender-validatie issue. Eerst sender fixen, dan pas opnieuw schalen.',
        })
    if kpi.get('total_campaigns', 0) == 0:
        recs.append({
            'priority': 'high',
            'type': 'action',
            'title': 'Eerste campagne versturen',
            'detail': 'Er zijn nog geen campagnes verstuurd. Start met testlijst → kleine warmte-batch → evaluatie.',
        })

    # Open rate benchmarks
    open_rate = kpi.get('open_rate', 0)
    if kpi.get('total_sent', 0) > 50:
        if open_rate < 15:
            recs.append({
                'priority': 'high',
                'type': 'optimize',
                'title': f'Open rate laag ({open_rate}%)',
                'detail': 'Overweeg subject line A/B test. Benchmark B2B NL: 20-30%.',
            })
        elif open_rate > 35:
            recs.append({
                'priority': 'info',
                'type': 'insight',
                'title': f'Open rate excellent ({open_rate}%)',
                'detail': 'Subject lines werken goed. Focus nu op click-through optimalisatie.',
            })

    # Click rate
    click_rate = kpi.get('click_rate', 0)
    if kpi.get('total_delivered', 0) > 50 and click_rate < 3:
        recs.append({
            'priority': 'medium',
            'type': 'optimize',
            'title': f'Click rate kan beter ({click_rate}%)',
            'detail': 'Check CTA zichtbaarheid en prijslijst-link prominentie. Benchmark: 3-8%.',
        })

    # Bounce health
    bounce_rate = kpi.get('bounce_rate', 0)
    if kpi.get('total_sent', 0) > 20 and bounce_rate > 5:
        recs.append({
            'priority': 'high',
            'type': 'hygiene',
            'title': f'Bounce rate te hoog ({bounce_rate}%)',
            'detail': 'Verwijder ongeldige emails. >5% schaadt deliverability.',
        })

    # Unsub rate
    unsub_rate = kpi.get('unsub_rate', 0)
    if kpi.get('total_delivered', 0) > 50 and unsub_rate > 2:
        recs.append({
            'priority': 'medium',
            'type': 'hygiene',
            'title': f'Unsubscribe rate hoog ({unsub_rate}%)',
            'detail': 'Check of segmentatie goed genoeg is. >2% = content/audience mismatch.',
        })

    # DB health
    leads_with_email = db.get('leads_with_email', 0)
    total = db.get('total_leads', 0)
    if total > 0 and leads_with_email / total < 0.5:
        recs.append({
            'priority': 'medium',
            'type': 'enrich',
            'title': f'Slechts {leads_with_email}/{total} leads hebben email',
            'detail': 'Verrijk leads via website scraping of handmatig research.',
        })

    # Hot prospects without follow-up
    hot = [p for p in db.get('hot_prospects', []) if (p.get('hot_score') or 0) >= 60]
    if hot:
        recs.append({
            'priority': 'high',
            'type': 'action',
            'title': f'{len(hot)} hot prospects wachten op opvolging',
            'detail': f'Top: {", ".join(p["company_name"] for p in hot[:3])}',
        })

    # Credits check
    credits = brevo.get('credits_remaining', 0)
    if isinstance(credits, (int, float)) and 0 < credits < 100:
        recs.append({
            'priority': 'high',
            'type': 'hygiene',
            'title': f'Brevo credits bijna op ({credits})',
            'detail': 'Upgrade plan of koop credits bij.',
        })

    return recs


def main() -> None:
    cfg = load_config()
    api_key, key_source = choose_brevo_key(cfg)

    print('▶ Fetching Brevo stats...')
    brevo = fetch_brevo_data(api_key, key_source)

    print('▶ Reading local DB...')
    db = fetch_db_stats()

    print('▶ Computing recommendations...')
    recs = compute_recommendations(brevo, db)

    combined = {
        'generated_at': utc_now(),
        'brevo': brevo,
        'db': db,
        'recommendations': recs,
    }

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(combined, indent=2, ensure_ascii=False, default=str) + '\n')
    print(f'✅ Wrote {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
