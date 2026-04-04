#!/usr/bin/env python3
"""Send test campaign emails via Brevo transactional API."""
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/partner-campaign')
CONFIG = json.loads((BASE / 'config.local.json').read_text())

API_KEY = CONFIG['brevo']['api_key']
SENDER_NAME = CONFIG['brevo']['sender_name']
SENDER_EMAIL = CONFIG['brevo']['sender_email']


def send_email(to_email: str, to_name: str, subject: str, html_file: str, tag: str) -> dict:
    html = (BASE / 'emails' / html_file).read_text(encoding='utf-8')
    
    payload = {
        "sender": {"name": SENDER_NAME, "email": SENDER_EMAIL},
        "to": [{"email": to_email, "name": to_name}],
        "subject": subject,
        "htmlContent": html,
        "replyTo": {"email": SENDER_EMAIL, "name": SENDER_NAME},
        "tags": [tag],
        "headers": {
            "X-Mailin-Tag": tag
        }
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        'https://api.brevo.com/v3/smtp/email',
        data=data,
        headers={
            'accept': 'application/json',
            'api-key': API_KEY,
            'content-type': 'application/json',
        },
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode('utf-8')
            return {'status': resp.status, 'response': json.loads(body) if body else {}, 'tag': tag}
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        return {'status': e.code, 'error': body, 'tag': tag}


def main():
    to_email = sys.argv[1] if len(sys.argv) > 1 else 'milan@nova-cell.com'
    to_name = sys.argv[2] if len(sys.argv) > 2 else 'Milan de Romijn'
    
    print(f"Sending 2 test variants to {to_email}...\n")
    
    # Variant A — Direct partnership, clean
    result_a = send_email(
        to_email=to_email,
        to_name=to_name,
        subject="Partner worden? Bekijk onze Deye-partnerprijslijst",
        html_file="campaign_mail_variant_a.html",
        tag="partner-launch-a"
    )
    print(f"Variant A: {json.dumps(result_a, indent=2)}\n")
    
    # Variant B — Product-first, premium feel
    result_b = send_email(
        to_email=to_email,
        to_name=to_name,
        subject="Deye partnertarieven voor installateurs — direct inzien",
        html_file="campaign_mail_variant_b.html",
        tag="partner-launch-b"
    )
    print(f"Variant B: {json.dumps(result_b, indent=2)}\n")
    
    # Summary
    ok = all(r.get('status') in (200, 201, 202) for r in [result_a, result_b])
    print(f"{'✅ Both sent successfully' if ok else '❌ One or more failed'}")
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
