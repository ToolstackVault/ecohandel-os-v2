#!/usr/bin/env python3
"""EcoHandel OS — Data Fetch Pipeline v3"""
from __future__ import annotations
import json, os, sqlite3, subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ENV_FILE = Path('/var/www/html/control.ecohandel.nl/.env')
if ENV_FILE.exists():
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())

BASE_DIR = Path('/var/www/html/control.ecohandel.nl/dashboard-data')
DATA_DIR = BASE_DIR / 'data'
DB_PATH = os.environ.get('ECOHANDEL_DB', '/var/www/html/control.ecohandel.nl/data/ecohandel.db')
GSC_SA = '/root/.openclaw/service-account-content-empire.json'

def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    print('  OK ' + path.name)

def api_get(url, headers=None, timeout=30):
    req = Request(url, headers=headers or {})
    try:
        with urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception as e:
        print('  API error ' + url + ': ' + str(e))
        return {}

def run_py(code, timeout=60):
    env = os.environ.copy()
    env['GOOGLE_APPLICATION_CREDENTIALS'] = GSC_SA
    r = subprocess.run(['/opt/ecohandel-venv/bin/python3', '-c', code],
                      capture_output=True, text=True, timeout=timeout, env=env)
    try:
        return json.loads(r.stdout.strip())
    except Exception:
        return {'error': r.stderr.strip() or r.stdout.strip()}

def fetch_gsc():
    code = """
import json
from google.oauth2 import service_account
import googleapiclient.discovery
from datetime import datetime, timezone, timedelta
try:
    creds = service_account.Credentials.from_service_account_file(
        '%s', scopes=['https://www.googleapis.com/auth/webmasters.readonly'])
    svc = googleapiclient.discovery.build('searchconsole', 'v1', credentials=creds)
    today = datetime.now(timezone.utc).date()
    start = (today - timedelta(days=28)).isoformat()
    end = today.isoformat()
    res = svc.searchanalytics().query(
        siteUrl='sc-domain:ecohandel.nl',
        body={'startDate': start, 'endDate': end, 'dimensions': ['query'],
              'rowLimit': 20, 'aggregationType': 'byPage'}).execute()
    rows = res.get('rows', [])
    top = []
    for row in rows[:10]:
        top.append({
            'query': row['keys'][0],
            'clicks': row['clicks'],
            'impressions': row['impressions'],
            'position': round(row['position'], 1)
        })
    total_clicks = sum(r['clicks'] for r in rows)
    total_impr = sum(r['impressions'] for r in rows)
    print(json.dumps({
        'clicks': total_clicks,
        'impressions': total_impr,
        'top_queries': top,
        'fetched_at': datetime.now(timezone.utc).isoformat()
    }))
except Exception as e:
    print(json.dumps({'error': str(e)}))
""" % GSC_SA
    return run_py(code)

def fetch_ga4():
    prop_id = os.environ.get('GA4_PROPERTY_ID', '529517517')
    code = """
import json
from google.oauth2 import service_account
import googleapiclient.discovery
from datetime import datetime, timezone, timedelta
try:
    creds = service_account.Credentials.from_service_account_file(
        '%s', scopes=['https://www.googleapis.com/auth/analytics.readonly'])
    svc = googleapiclient.discovery.build('analyticsdata', 'v2beta', credentials=creds)
    today = datetime.now(timezone.utc).date()
    start = (today - timedelta(days=28)).isoformat()
    end = today.isoformat()
    res = svc.properties().runReport(
        property='properties/%s',
        body={'dateRanges': [{'startDate': start, 'endDate': end}],
              'metrics': [{'name': 'sessions'}, {'name': 'totalRevenue'}, {'name': 'conversions'}]}).execute()
    rows = res.get('rows', [])
    data = {'sessions': 0, 'revenue': 0.0, 'conversions': 0, 'fetched_at': datetime.now(timezone.utc).isoformat()}
    if rows:
        data['sessions'] = int(rows[0]['metricValues'][0]['value'])
        data['revenue'] = float(rows[0]['metricValues'][1]['value'])
        data['conversions'] = int(rows[0]['metricValues'][2]['value'])
    print(json.dumps(data))
except Exception as e:
    print(json.dumps({'error': str(e)}))
""" % (GSC_SA, prop_id)
    return run_py(code)

def fetch_shopify():
    token = os.environ.get('SHOPIFY_ADMIN_TOKEN', '')
    shop = os.environ.get('SHOPIFY_STORE_URL', 'n6f6ja-qr.myshopify.com')
    if not token:
        return {'orders_today': 0, 'revenue_today': 0.0, 'error': 'no_token'}
    code = """
import json, urllib.request
from datetime import datetime, timezone
TOKEN = '%s'
SHOP = '%s'
today = datetime.now(timezone.utc).date().isoformat()
url = 'https://' + SHOP + '/admin/api/2026-01/orders.json?status=any&created_at_min=' + today + 'T00:00:00Z&limit=250'
req = urllib.request.Request(url, headers={'X-Shopify-Access-Token': TOKEN})
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read())
orders = data.get('orders', [])
revenue = sum(float(o.get('total_price', 0)) for o in orders)
print(json.dumps({
    'orders_today': len(orders),
    'revenue_today': round(revenue, 2),
    'fetched_at': datetime.now(timezone.utc).isoformat()
}))
""" % (token, shop)
    return run_py(code, timeout=30)

def fetch_wefact():
    key = os.environ.get('WEFACT_API_KEY', '')
    url = os.environ.get('WEFACT_BASE_URL', 'https://api.mijnwefact.nl/v2')
    if not key:
        return {'omzet': 0, 'openstaand': 0, 'facturen': 0, 'error': 'no_api_key'}
    data = api_get(url + '/invoice?api_key=' + key + '&limit=50')
    if 'result' not in data:
        return {'omzet': 0, 'error': 'api_error'}
    invoices = data.get('result', [])
    now = datetime.now(timezone.utc)
    this_month = [i for i in invoices if i.get('DateOfIssue', '').startswith(now.strftime('%Y-%m'))]
    return {
        'omzet': round(sum(float(i.get('TotalExcl', 0)) for i in this_month), 2),
        'openstaand': round(sum(float(i.get('TotalExcl', 0)) for i in invoices if i.get('status') in ('sent', 'partial')), 2),
        'facturen_maand': len(this_month),
        'facturen_totaal': len(invoices),
        'fetched_at': utc_now()
    }

def fetch_brevo():
    key = os.environ.get('BREVO_API_KEY', '')
    if not key:
        return {'total_contacts': 0, 'error': 'no_api_key'}
    headers = {'api-key': key}
    contacts = api_get('https://api.brevo.com/v3/contacts/count', headers=headers)
    campaigns = api_get('https://api.brevo.com/v3/emailCampaigns?limit=5', headers=headers)
    return {
        'total_contacts': contacts.get('count', 0),
        'campaigns': len(campaigns.get('campaigns', [])),
        'fetched_at': utc_now()
    }

def fetch_ads():
    return {'spend_today': 0, 'spend_28d': 0, 'conversions_28d': 0, 'error': 'needs_config'}

def fetch_health():
    checks = {'api': 'ok', 'db': 'ok', 'vps_disk_ok': True}
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('SELECT 1').fetchone()
        conn.close()
    except Exception:
        checks['db'] = 'error'
    try:
        r = subprocess.run(['df', '-h', '/'], capture_output=True, text=True, timeout=5)
        usage = int(r.stdout.split('\n')[1].split()[4].rstrip('%'))
        checks['disk_usage_pct'] = usage
        checks['vps_disk_ok'] = usage < 90
    except Exception:
        pass
    healthy = all(v == 'ok' or v is True for v in checks.values())
    return {
        'status': 'healthy' if healthy else 'degraded',
        'checks': checks,
        'fetched_at': utc_now()
    }

def main():
    print('\n=== EcoHandel OS Data Fetch — ' + utc_now() + ' ===\n')
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name, fn in [
        ('GSC', fetch_gsc), ('GA4', fetch_ga4), ('Shopify', fetch_shopify),
        ('WeFact', fetch_wefact), ('Brevo', fetch_brevo), ('Ads', fetch_ads)
    ]:
        print('Fetching ' + name + '...')
        write_json(DATA_DIR / (name.lower() + '.json'), fn())
    print('Health...')
    write_json(DATA_DIR / 'health.json', fetch_health())
    write_json(DATA_DIR / 'meta.json', {'version': '2.0', 'rendered_at': utc_now()})
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        total, top5, done = conn.execute(
            "SELECT COUNT(*), SUM(lane='top_5_now'), SUM(status='done') FROM queue_items").fetchone()
        conn.close()
        write_json(DATA_DIR / 'queue_summary.json',
                   {'total': total, 'top_5': top5, 'done': done, 'fetched_at': utc_now()})
    except Exception as e:
        print('  queue_summary error: ' + str(e))
    print('\n=== Done — ' + utc_now() + ' ===\n')

if __name__ == '__main__':
    main()
