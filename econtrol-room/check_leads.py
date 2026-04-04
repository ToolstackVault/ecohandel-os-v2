#!/usr/bin/env python3
"""Check partner leads in ndjson file."""
import json

with open('/var/www/html/control.ecohandel.nl/data/partner-aanvragen.ndjson') as f:
    lines = [json.loads(l) for l in f]

print(f"Total leads: {len(lines)}")
for l in lines[:10]:
    print(f"  {l.get('email','no-email')} | {l.get('company_name','')} | {l.get('status','')}")
