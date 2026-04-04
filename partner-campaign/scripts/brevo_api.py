#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/partner-campaign')
CONFIG_PATH = BASE / 'config.local.json'


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise SystemExit(f'Missing config: {CONFIG_PATH}')
    return json.loads(CONFIG_PATH.read_text(encoding='utf-8'))


def brevo_request(method: str, path: str, payload: dict | None = None, query: dict | None = None) -> tuple[int, object]:
    cfg = load_config()
    api_key = cfg['brevo']['api_key']
    url = 'https://api.brevo.com/v3' + path
    if query:
        url += '?' + urllib.parse.urlencode(query)

    data = None
    headers = {
        'accept': 'application/json',
        'api-key': api_key,
    }
    if payload is not None:
        data = json.dumps(payload).encode('utf-8')
        headers['content-type'] = 'application/json'

    req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode('utf-8')
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        try:
            parsed = json.loads(body) if body else {}
        except Exception:
            parsed = {'raw': body}
        return e.code, parsed


def print_json(data: object) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_status(_: argparse.Namespace) -> int:
    status, account = brevo_request('GET', '/account')
    if status >= 400:
        print_json({'ok': False, 'status': status, 'error': account})
        return 1

    sender_status, senders = brevo_request('GET', '/senders')
    list_status, lists = brevo_request('GET', '/contacts/lists', query={'limit': 50, 'offset': 0})
    camp_status, campaigns = brevo_request('GET', '/emailCampaigns', query={'limit': 10, 'offset': 0})

    summary = {
        'ok': True,
        'account_email': account.get('email'),
        'company_name': account.get('companyName'),
        'sender_count': len(senders.get('senders', [])) if isinstance(senders, dict) else None,
        'list_count': len(lists.get('lists', [])) if isinstance(lists, dict) else None,
        'recent_campaign_count': len(campaigns.get('campaigns', [])) if isinstance(campaigns, dict) else None,
        'statuses': {
            'account': status,
            'senders': sender_status,
            'lists': list_status,
            'campaigns': camp_status,
        },
    }
    print_json(summary)
    return 0


def cmd_lists(args: argparse.Namespace) -> int:
    status, payload = brevo_request('GET', '/contacts/lists', query={'limit': args.limit, 'offset': args.offset})
    print_json({'status': status, 'payload': payload})
    return 0 if status < 400 else 1


def cmd_campaigns(args: argparse.Namespace) -> int:
    status, payload = brevo_request('GET', '/emailCampaigns', query={'limit': args.limit, 'offset': args.offset})
    print_json({'status': status, 'payload': payload})
    return 0 if status < 400 else 1


def cmd_create_list(args: argparse.Namespace) -> int:
    payload = {'name': args.name}
    if args.folder_id is not None:
        payload['folderId'] = args.folder_id
    status, result = brevo_request('POST', '/contacts/lists', payload=payload)
    print_json({'status': status, 'payload': result})
    return 0 if status < 400 else 1


def normalize_email(value: str | None) -> str | None:
    if not value:
        return None
    email = value.strip().lower()
    return email or None


def normalize_phone(value: str | None) -> str | None:
    if not value:
        return None
    raw = str(value).strip()
    cleaned = ''.join(ch for ch in raw if ch.isdigit() or ch == '+')
    if cleaned.startswith('00'):
        cleaned = '+' + cleaned[2:]
    if cleaned.startswith('+'):
        digits = ''.join(ch for ch in cleaned if ch.isdigit())
        if 8 <= len(digits) <= 15:
            return '+' + digits
        return None
    digits = ''.join(ch for ch in cleaned if ch.isdigit())
    if len(digits) == 10 and digits.startswith('0'):
        return '+31' + digits[1:]
    return None


def pick_attrs(row: dict) -> dict:
    attrs = {}
    lowered = {str(k).strip().lower(): v for k, v in row.items()}

    simple_mapping = {
        'FIRSTNAME': ['first_name', 'firstname', 'voornaam'],
        'LASTNAME': ['last_name', 'lastname', 'achternaam'],
        'COMPANY': ['company', 'bedrijf', 'company_name'],
    }
    for target, keys in simple_mapping.items():
        for key in keys:
            value = lowered.get(key)
            if value:
                attrs[target] = str(value).strip()
                break

    for key in ['phone', 'telefoon', 'mobile', 'mobiel']:
        value = lowered.get(key)
        normalized = normalize_phone(value)
        if normalized:
            attrs['SMS'] = normalized
            break

    return attrs


def cmd_import_csv(args: argparse.Namespace) -> int:
    path = Path(args.csv_file)
    if not path.exists():
        print_json({'ok': False, 'error': f'CSV not found: {path}'})
        return 1

    created = 0
    updated = 0
    skipped = 0
    errors = []

    with path.open(newline='', encoding=args.encoding) as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=2):
            email = normalize_email(row.get(args.email_column) or row.get(args.email_column.lower()) or row.get(args.email_column.upper()))
            if not email:
                skipped += 1
                continue

            payload = {
                'email': email,
                'attributes': pick_attrs(row),
                'emailBlacklisted': False,
                'smsBlacklisted': True,
                'updateEnabled': True,
                'listIds': [args.list_id],
            }
            status, result = brevo_request('POST', '/contacts', payload=payload)
            if status in (200, 201, 204):
                created += 1
            elif status == 400 and isinstance(result, dict) and str(result.get('code', '')).lower() in {'duplicate_parameter', 'duplicate_request'}:
                updated += 1
            elif status == 400 and isinstance(result, dict) and 'Contact already exist' in json.dumps(result):
                updated += 1
            else:
                errors.append({'line': idx, 'email': email, 'status': status, 'error': result})

    print_json({
        'ok': len(errors) == 0,
        'list_id': args.list_id,
        'csv_file': str(path),
        'created_or_upserted': created,
        'probable_existing_updated': updated,
        'skipped': skipped,
        'errors': errors[:20],
        'error_count': len(errors),
    })
    return 0 if len(errors) == 0 else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='EcoHandel Brevo API beheerlaag')
    sub = parser.add_subparsers(dest='command', required=True)

    p = sub.add_parser('status', help='Check account, senders, lists en campagnes')
    p.set_defaults(func=cmd_status)

    p = sub.add_parser('lists', help='Toon contactlijsten')
    p.add_argument('--limit', type=int, default=50)
    p.add_argument('--offset', type=int, default=0)
    p.set_defaults(func=cmd_lists)

    p = sub.add_parser('campaigns', help='Toon recente emailcampagnes')
    p.add_argument('--limit', type=int, default=20)
    p.add_argument('--offset', type=int, default=0)
    p.set_defaults(func=cmd_campaigns)

    p = sub.add_parser('create-list', help='Maak een Brevo lijst aan')
    p.add_argument('name')
    p.add_argument('--folder-id', type=int)
    p.set_defaults(func=cmd_create_list)

    p = sub.add_parser('import-csv', help='Importeer contacten uit CSV naar een Brevo lijst')
    p.add_argument('list_id', type=int)
    p.add_argument('csv_file')
    p.add_argument('--email-column', default='email')
    p.add_argument('--encoding', default='utf-8')
    p.set_defaults(func=cmd_import_csv)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
