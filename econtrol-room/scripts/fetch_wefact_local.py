#!/usr/bin/env python3
"""EcoHandel WeFact fetch — runs on Mac Mini (84.85.55.133 = whitelisted).
"""
import json, os, subprocess
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/econtrol-room/dashboard-data/data')
BASE.mkdir(parents=True, exist_ok=True)

# Load from env file, fallback to hardcoded key
ENV_FILE = Path('/Users/ecohandel.nl/.openclaw/workspace/.env/apis.env')
for line in ENV_FILE.read_text().splitlines():
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip())

# Defensive: override TO_BE_SET placeholders
KEY = os.environ.get('WEFACT_API_KEY', '')
if KEY in ('TO_BE_SET', '', 'changeme'):
    KEY = '252d7a747d3e64dbbd8707a964beabed'

URL = 'https://api.mijnwefact.nl/v2/'

def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')

def curl_post(data_dict):
    parts = ' '.join(f'-d {k}={v}' for k, v in data_dict.items())
    cmd = f"curl -s -X POST '{URL}' {parts}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return json.loads(result.stdout)

def write(name, data):
    path = BASE / name
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    print(f'  OK {name}')

def main():
    print(f'=== WeFact fetch — {utc_now()} ===')

    raw = curl_post({'api_key': KEY, 'controller': 'invoice', 'action': 'list', 'limit': 100})
    invoices = raw.get('invoices', []) if isinstance(raw, dict) else []
    print(f'  Invoices total: {len(invoices)}')

    now = datetime.now(timezone.utc)
    this_month = [i for i in invoices if str(i.get('Date', '')).startswith(now.strftime('%Y-%m'))]
    paid = [i for i in invoices if str(i.get('Status', '')) == '8']
    open_inv = [i for i in invoices if str(i.get('Status', '')) in ('2', '3', '5')]
    openstaand = sum(float(i.get('AmountOutstanding', 0) or 0) for i in invoices
                     if str(i.get('Status', '')) not in ('4', '8', '9'))

    write('wefact.json', {
        'omzet': round(sum(float(i.get('AmountExcl', 0)) for i in this_month), 2),
        'omzet_totaal': round(sum(float(i.get('AmountExcl', 0)) for i in invoices), 2),
        'openstaand': round(openstaand, 2),
        'facturen_maand': len(this_month),
        'facturen_totaal': len(invoices),
        'facturen_betaald': len(paid),
        'facturen_open': len(open_inv),
        'paid': paid[:5],
        'open': open_inv[:10],
        'recent': this_month[:10],
        'fetched_at': utc_now()
    })

    try:
        q_raw = curl_post({'api_key': KEY, 'controller': 'pricequote', 'action': 'list', 'limit': 20})
        quotes = q_raw.get('pricequote', []) if isinstance(q_raw, dict) else []
        quotes_open = [q for q in quotes if str(q.get('Status', '')) in ('1', '2', '3')]
        write('wefact_quotes.json', {
            'offerte_totaal': len(quotes),
            'offerte_open': len(quotes_open),
            'open': quotes_open[:10],
            'fetched_at': utc_now()
        })
    except Exception as e:
        print(f'  SKIP quotes: {e}')

    print(f'=== Done — {utc_now()} ===')

if __name__ == '__main__':
    main()
