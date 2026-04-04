#!/usr/bin/env python3
"""Send a partner campaign batch via Brevo Campaigns API.

Flow:
  1. Find or create Brevo contact list for this batch.
  2. Import leads into the list (unsubscribed contacts skipped).
  3. Find or create Brevo email campaign targeting the list.
  4. Send campaign (or dry-run: stop before final send).
  5. Update local DB: list_id, campaign_id, lead send statuses.

Usage:
  python send_batch_campaign.py B1
  python send_batch_campaign.py B1 --dry-run
  python send_batch_campaign.py B1 --test-email milan@nova-cell.com
"""
from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/partner-campaign')
CONFIG = json.loads((BASE / 'config.local.json').read_text(encoding='utf-8'))
DB_PATH = BASE / 'data' / 'partner_campaign.db'
LAUNCH_DIR = BASE / 'launch'
EMAILS_DIR = BASE / 'emails'

SENDER_NAME = CONFIG['brevo']['sender_name']
SENDER_EMAIL = CONFIG['brevo']['sender_email']
API_KEY = CONFIG['brevo']['api_key']
ECO_LOGO_URL = CONFIG['brevo']['pricelist_logo_eco']
DEYE_LOGO_URL = CONFIG['brevo']['pricelist_logo_deye']

VARIANT_MAP = {
    'A': 'campaign_mail_variant_a.html',
    'B': 'campaign_mail_variant_b.html',
    'B-challenger': 'campaign_mail_variant_b.html',
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def log(msg: str) -> None:
    ts = datetime.now().strftime('%H:%M:%S')
    print(f'[{ts}] {msg}', flush=True)


def brevo_request(method: str, path: str, payload: dict | None = None, query: dict | None = None) -> tuple[int, object]:
    url = 'https://api.brevo.com/v3' + path
    if query:
        url += '?' + urllib.parse.urlencode(query)
    data = None
    headers = {'accept': 'application/json', 'api-key': API_KEY}
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


def normalize_email(value: str | None) -> str:
    return (value or '').strip().lower()


def assert_public_asset(url: str, label: str) -> None:
    req = urllib.request.Request(url, headers={'User-Agent': 'OpenClaw/1.0'}, method='HEAD')
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = getattr(resp, 'status', 200)
            ctype = (resp.headers.get('Content-Type') or '').lower()
            if status >= 400:
                raise SystemExit(f'{label} asset check failed: HTTP {status} for {url}')
            if 'image/' not in ctype:
                raise SystemExit(f'{label} asset check failed: expected image/*, got {ctype or "unknown"} for {url}')
    except urllib.error.HTTPError as e:
        raise SystemExit(f'{label} asset check failed: HTTP {e.code} for {url}') from e
    except Exception as e:
        raise SystemExit(f'{label} asset check failed for {url}: {e}') from e


# ── STEP 1: BREVO LIST MANAGEMENT ─────────────────────────────────────────────

def find_brevo_list(list_name: str) -> int | None:
    """Return existing Brevo list ID by name, or None."""
    offset = 0
    while True:
        status, payload = brevo_request('GET', '/contacts/lists', query={'limit': 50, 'offset': offset})
        if status >= 400:
            raise SystemExit(f'Failed to fetch Brevo lists: {status} {payload}')
        data = payload if isinstance(payload, dict) else {}
        lists = data.get('lists', [])
        for lst in lists:
            if lst.get('name') == list_name:
                return lst['id']
        total = data.get('count', 0)
        offset += 50
        if offset >= total or not lists:
            break
    return None


def create_brevo_list(list_name: str) -> int:
    """Create a new Brevo contact list and return its ID."""
    status, payload = brevo_request('POST', '/contacts/lists', payload={
        'name': list_name,
        'folderId': 1,
    })
    if status not in (200, 201):
        raise SystemExit(f'Failed to create Brevo list "{list_name}": {status} {payload}')
    list_id = payload.get('id') if isinstance(payload, dict) else None
    if not list_id:
        raise SystemExit(f'No list ID in response: {payload}')
    return list_id


def get_or_create_list(list_name: str) -> tuple[int, bool]:
    """Return (list_id, was_created)."""
    existing = find_brevo_list(list_name)
    if existing:
        log(f'  Found existing list "{list_name}" (id={existing})')
        return existing, False
    list_id = create_brevo_list(list_name)
    log(f'  Created new list "{list_name}" (id={list_id})')
    return list_id, True


# ── STEP 2: CONTACT IMPORT ────────────────────────────────────────────────────

def parse_name(contact_person: str) -> tuple[str, str]:
    parts = (contact_person or '').strip().split(' ', 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return parts[0] if parts else '', ''


def import_contact(email: str, first_name: str, last_name: str, company: str, list_id: int) -> tuple[int, object]:
    """Upsert a single Brevo contact and add to list."""
    payload = {
        'email': email,
        'attributes': {
            'FIRSTNAME': first_name,
            'LASTNAME': last_name,
            'COMPANY': company,
        },
        'listIds': [list_id],
        'updateEnabled': True,
    }
    return brevo_request('POST', '/contacts', payload=payload)


def import_contacts_to_list(rows: list[dict], list_id: int, test_email: str | None) -> dict:
    """Import all batch leads into the Brevo list. Returns summary dict."""
    results: dict = {'imported': [], 'skipped': [], 'errors': []}

    targets = rows
    if test_email:
        targets = [{'email': test_email, 'contact_person': '', 'company_name': 'Nova Cell (test)'}]

    for row in targets:
        email = normalize_email(row.get('email'))
        if not email:
            results['skipped'].append({'email': email, 'reason': 'empty_email'})
            continue

        company = (row.get('company_name') or '').strip()
        first, last = parse_name(row.get('contact_person') or '')

        status, result = import_contact(email, first, last, company, list_id)
        log(f'  import {email}: HTTP {status} → {json.dumps(result, ensure_ascii=False)[:140]}')

        if status in (200, 201):
            results['imported'].append({'email': email, 'company': company})
        elif status == 204:
            # Updated existing contact (no body returned)
            results['imported'].append({'email': email, 'company': company, 'updated': True})
        elif status == 400:
            err = result if isinstance(result, dict) else {}
            code = err.get('code', '')
            # duplicate_parameter means contact is blacklisted/unsubscribed in Brevo
            if code == 'duplicate_parameter':
                results['skipped'].append({'email': email, 'reason': 'unsubscribed_or_blacklisted', 'detail': err})
            else:
                results['errors'].append({'email': email, 'status': status, 'detail': result})
        else:
            results['errors'].append({'email': email, 'status': status, 'detail': result})

        time.sleep(0.15)  # Brevo rate limiting

    return results


# ── STEP 3: CAMPAIGN MANAGEMENT ───────────────────────────────────────────────

def find_brevo_campaign(campaign_name: str) -> int | None:
    """Return existing Brevo campaign ID by name, searching all statuses."""
    for campaign_status in ('draft', 'queued', 'sent', 'suspended', 'archive'):
        offset = 0
        while True:
            status, payload = brevo_request('GET', '/emailCampaigns', query={
                'limit': 50, 'offset': offset, 'status': campaign_status,
            })
            if status >= 400:
                break
            data = payload if isinstance(payload, dict) else {}
            campaigns = data.get('campaigns', [])
            for c in campaigns:
                if c.get('name') == campaign_name:
                    return c['id']
            total = data.get('count', 0)
            offset += 50
            if offset >= total or not campaigns:
                break
    return None


def create_brevo_campaign(name: str, subject: str, html_content: str,
                          list_id: int, campaign_key: str) -> int:
    """Create a Brevo email campaign. Returns numeric campaign ID."""
    payload = {
        'name': name,
        'subject': subject,
        'sender': {'name': SENDER_NAME, 'email': SENDER_EMAIL},
        'type': 'classic',
        'htmlContent': html_content,
        'replyTo': SENDER_EMAIL,
        'recipients': {'listIds': [list_id]},
        'utmCampaign': campaign_key,
    }
    status, result = brevo_request('POST', '/emailCampaigns', payload=payload)
    if status not in (200, 201):
        raise SystemExit(f'Failed to create campaign "{name}": {status} {result}')
    cid = result.get('id') if isinstance(result, dict) else None
    if not cid:
        raise SystemExit(f'No campaign ID in response: {result}')
    return cid


def update_campaign(brevo_campaign_id: int, list_id: int, subject: str, html_content: str, campaign_key: str) -> None:
    """Refresh an existing campaign so content, tracking and recipients stay current."""
    status, result = brevo_request('PUT', f'/emailCampaigns/{brevo_campaign_id}', payload={
        'subject': subject,
        'htmlContent': html_content,
        'recipients': {'listIds': [list_id]},
        'utmCampaign': campaign_key,
    })
    log(f'  Updated campaign {brevo_campaign_id}: HTTP {status} {json.dumps(result, ensure_ascii=False)[:160]}')


def get_or_create_campaign(campaign_name: str, subject: str, html_content: str,
                            list_id: int, campaign_key: str) -> tuple[int, bool]:
    """Return (brevo_campaign_id, was_created)."""
    existing = find_brevo_campaign(campaign_name)
    if existing:
        log(f'  Found existing campaign "{campaign_name}" (id={existing})')
        update_campaign(existing, list_id, subject, html_content, campaign_key)
        return existing, False
    brevo_id = create_brevo_campaign(campaign_name, subject, html_content, list_id, campaign_key)
    log(f'  Created new campaign "{campaign_name}" (id={brevo_id})')
    return brevo_id, True


# ── STEP 4: LOCAL DB ──────────────────────────────────────────────────────────

def open_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Ensure brevo_list_id column exists (schema migration)
    cols = [r[1] for r in conn.execute('PRAGMA table_info(campaigns)').fetchall()]
    if 'brevo_list_id' not in cols:
        conn.execute('ALTER TABLE campaigns ADD COLUMN brevo_list_id INTEGER')
        conn.commit()
        log('  Migrated DB: added brevo_list_id column to campaigns')
    return conn


def ensure_campaign_db(conn: sqlite3.Connection, campaign_key: str, subject: str,
                        batch: dict, html_file: str, brevo_campaign_id: int,
                        brevo_list_id: int, list_name: str) -> int:
    """Upsert local campaigns row. Returns local campaign id."""
    now = utc_now()
    notes = json.dumps({
        'batch': batch['batch'],
        'html_file': html_file,
        'brevo_campaign_id': brevo_campaign_id,
        'brevo_list_id': brevo_list_id,
    })
    row = conn.execute('SELECT id FROM campaigns WHERE brevo_campaign_id = ?', (campaign_key,)).fetchone()
    if row:
        conn.execute(
            'UPDATE campaigns SET subject_line=?, sender_name=?, sender_email=?, status=?, '
            'list_name=?, brevo_list_id=?, notes=?, updated_at=? WHERE id=?',
            (subject, SENDER_NAME, SENDER_EMAIL, 'ready', list_name, brevo_list_id, notes, now, row['id'])
        )
        conn.commit()
        return row['id']
    conn.execute(
        '''INSERT INTO campaigns
             (brevo_campaign_id, name, campaign_type, subject_line, sender_name, sender_email,
              status, list_name, brevo_list_id, cta_primary, price_list_url, notes, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (campaign_key, campaign_key, 'partner-outreach', subject, SENDER_NAME, SENDER_EMAIL,
         'ready', list_name, brevo_list_id, 'Bekijk de partnerprijslijst',
         CONFIG['brevo']['pricelist_url'], notes, now, now)
    )
    conn.commit()
    return conn.execute('SELECT id FROM campaigns WHERE brevo_campaign_id = ?', (campaign_key,)).fetchone()['id']


def mark_leads_sent(conn: sqlite3.Connection, local_campaign_id: int,
                    imported_emails: list[str], dry_run: bool) -> list[dict]:
    """Upsert lead_campaigns rows for imported contacts."""
    now = utc_now()
    send_status = 'queued' if dry_run else 'sent'
    results = []

    for email in imported_emails:
        lead = conn.execute('SELECT id FROM leads WHERE lower(email) = lower(?) LIMIT 1', (email,)).fetchone()
        if not lead:
            results.append({'email': email, 'action': 'skipped', 'reason': 'not_in_local_db'})
            continue
        lead_id = lead['id']
        existing = conn.execute(
            'SELECT id FROM lead_campaigns WHERE lead_id = ? AND campaign_id = ?',
            (lead_id, local_campaign_id)
        ).fetchone()
        if existing:
            conn.execute(
                'UPDATE lead_campaigns SET send_status=?, sent_at=?, last_event_at=?, updated_at=? WHERE id=?',
                (send_status, now if not dry_run else None, now, now, existing['id'])
            )
            results.append({'email': email, 'action': 'updated', 'lead_id': lead_id, 'send_status': send_status})
        else:
            conn.execute(
                '''INSERT INTO lead_campaigns
                     (lead_id, campaign_id, send_status, sent_at, last_event_at, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (lead_id, local_campaign_id, send_status,
                 now if not dry_run else None, now if not dry_run else None, now, now)
            )
            results.append({'email': email, 'action': 'inserted', 'lead_id': lead_id, 'send_status': send_status})

        if not dry_run:
            conn.execute(
                "UPDATE leads SET status='sent', last_activity_at=?, updated_at=? "
                "WHERE id=? AND status NOT IN ('replied','unsubscribed','bounced')",
                (now, now, lead_id)
            )

    conn.commit()
    return results


# ── SCHEDULE HELPERS ──────────────────────────────────────────────────────────

def load_schedule(schedule_file: str | None = None) -> tuple[dict, Path]:
    schedule_path = Path(schedule_file) if schedule_file else (LAUNCH_DIR / '2026-03-28_send_schedule_locked.json')
    if not schedule_path.is_absolute():
        schedule_path = (BASE / schedule_path).resolve()
    data = json.loads(schedule_path.read_text(encoding='utf-8'))
    return data, schedule_path.parent


def find_batch(batch_name: str, schedule_file: str | None = None) -> tuple[dict, Path]:
    schedule, base_dir = load_schedule(schedule_file)
    for batch in schedule.get('batches', []):
        if batch.get('batch') == batch_name:
            return batch, base_dir
    available = ', '.join(str(b.get('batch')) for b in schedule.get('batches', []))
    raise SystemExit(f'Unknown batch: {batch_name}. Available: {available}')


def load_batch_rows(base_dir: Path, csv_rel: str) -> list[dict]:
    path = (base_dir / csv_rel).resolve()
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description='EcoHandel partner batch sender via Brevo Campaigns API')
    parser.add_argument('batch', help='Batch name: B1, B2, or B3')
    parser.add_argument('--dry-run', action='store_true', help='All steps except final send')
    parser.add_argument('--test-email', metavar='EMAIL',
                        help='Send only to this address (creates a separate TEST list/campaign)')
    parser.add_argument('--schedule-file', help='Optional schedule JSON path for dynamic daily batches')
    args = parser.parse_args()

    batch, schedule_base_dir = find_batch(args.batch, args.schedule_file)
    html_file = VARIANT_MAP[batch['variant']]
    campaign_key = batch['campaign_key']
    subject = batch['subject']
    rows = load_batch_rows(schedule_base_dir, batch['csv_file'])

    log('=' * 60)
    log('EcoHandel Partner Campaign Sender  —  Brevo Campaigns API')
    log('=' * 60)
    log(f'Batch        : {args.batch}')
    log(f'Campaign key : {campaign_key}')
    log(f'Variant      : {batch["variant"]} ({html_file})')
    log(f'Subject      : {subject}')
    log(f'Leads in CSV : {len(rows)}')
    if args.dry_run:
        log('[DRY RUN] Final send will be skipped')
    if args.test_email:
        log(f'[TEST MODE] Recipients overridden → {args.test_email}')
    log('')

    report: dict = {
        'batch': args.batch,
        'campaign_key': campaign_key,
        'dry_run': args.dry_run,
        'test_email': args.test_email,
        'csv_rows': len(rows),
    }

    # ── 1 / List management ─────────────────────────────────────────────────
    test_suffix = datetime.now().strftime('%Y%m%d-%H%M%S') if args.test_email else None
    suffix = f'TEST-{args.batch}-{test_suffix}' if args.test_email else f'BATCH_{args.batch}'
    list_name = f'EcoHandel Partner Campaign - {suffix}'
    log(f'[1/5] List management: "{list_name}"')
    list_id, list_created = get_or_create_list(list_name)
    report['brevo_list_id'] = list_id
    report['list_name'] = list_name
    report['list_created'] = list_created
    log(f'  → list_id={list_id} ({"created" if list_created else "found existing"})')

    # ── 2 / Contact import ──────────────────────────────────────────────────
    log(f'\n[2/5] Contact import → Brevo list {list_id}')
    import_results = import_contacts_to_list(rows, list_id, test_email=args.test_email)
    report['import'] = import_results
    log(f'  → imported: {len(import_results["imported"])}, '
        f'skipped: {len(import_results["skipped"])}, '
        f'errors: {len(import_results["errors"])}')

    # ── 3 / Campaign management ─────────────────────────────────────────────
    name_prefix = f'TEST-{test_suffix}-' if args.test_email else ''
    campaign_name = f'EcoHandel Partner Campaign - {name_prefix}{campaign_key}'
    html_content = (EMAILS_DIR / html_file).read_text(encoding='utf-8')
    assert_public_asset(ECO_LOGO_URL, 'EcoHandel logo')
    assert_public_asset(DEYE_LOGO_URL, 'Deye logo')
    html_content = (
        html_content
        .replace('__CAMPAIGN_KEY__', campaign_key)
        .replace('__ECO_LOGO_URL__', ECO_LOGO_URL)
        .replace('__DEYE_LOGO_URL__', DEYE_LOGO_URL)
    )
    log(f'\n[3/5] Campaign management: "{campaign_name}"')
    brevo_campaign_id, campaign_created = get_or_create_campaign(
        campaign_name, subject, html_content, list_id, campaign_key
    )
    report['brevo_campaign_id'] = brevo_campaign_id
    report['campaign_created'] = campaign_created
    log(f'  → brevo_campaign_id={brevo_campaign_id} '
        f'({"created" if campaign_created else "found existing, list updated"})')

    # ── 4 / Local DB update ─────────────────────────────────────────────────
    log(f'\n[4/5] Local DB update')
    conn = open_db()
    imported_emails = [e['email'] for e in import_results['imported']]
    if args.dry_run:
        local_campaign_id = None
        db_results = []
        report['local_campaign_id'] = None
        report['db_updates'] = []
        log('  [DRY RUN] No local DB reservation/write performed')
    else:
        local_campaign_id = ensure_campaign_db(
            conn, campaign_key, subject, batch, html_file,
            brevo_campaign_id, list_id, list_name
        )
        db_results = mark_leads_sent(conn, local_campaign_id, imported_emails, dry_run=args.dry_run)
        report['local_campaign_id'] = local_campaign_id
        report['db_updates'] = db_results
        log(f'  → local_campaign_id={local_campaign_id}, {len(db_results)} lead_campaigns rows updated')
        for r in db_results:
            log(f'    {r["email"]:45s} action={r.get("action")} status={r.get("send_status", "n/a")}')

    # ── 5 / Send ────────────────────────────────────────────────────────────
    log(f'\n[5/5] Send')
    if args.dry_run:
        log(f'  [DRY RUN] Skipping sendNow. Campaign {brevo_campaign_id} is a draft in Brevo.')
        report['send'] = {
            'status': 'dry_run',
            'message': f'Campaign id={brevo_campaign_id} ready in Brevo — not sent',
        }
    else:
        log(f'  Calling POST /emailCampaigns/{brevo_campaign_id}/sendNow ...')
        send_status, send_result = brevo_request('POST', f'/emailCampaigns/{brevo_campaign_id}/sendNow')
        log(f'  → HTTP {send_status}: {json.dumps(send_result, ensure_ascii=False)[:200]}')
        report['send'] = {'http_status': send_status, 'result': send_result}

        if send_status in (200, 201, 202, 204):
            log('  Campaign sent successfully!')
            if local_campaign_id is not None:
                conn.execute(
                    'UPDATE campaigns SET status=?, updated_at=? WHERE id=?',
                    ('sent', utc_now(), local_campaign_id)
                )
                conn.execute(
                    'UPDATE lead_campaigns SET send_status=?, sent_at=?, updated_at=? '
                    'WHERE campaign_id=? AND send_status IN (?,?)',
                    ('sent', utc_now(), utc_now(), local_campaign_id, 'queued', 'ready')
                )
                conn.commit()
        else:
            log(f'  Send FAILED — see report.send for details')

    log('\n' + '=' * 60)
    log('FINAL REPORT')
    log('=' * 60)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
