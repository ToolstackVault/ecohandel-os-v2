#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo
import urllib.request
import urllib.error

WS = Path('/Users/ecohandel.nl/.openclaw/workspace')
BASE = WS / 'ecohandel' / 'partner-campaign'
DB_PATH = BASE / 'data' / 'partner_campaign.db'
STATE_PATH = WS / 'ecohandel' / 'econtrol-room' / 'state' / 'partner-campaign-live.json'
FETCH_STATS = BASE / 'scripts' / 'fetch_brevo_stats.py'
DAILY_ROOT = BASE / 'launch' / 'daily'
LEARNINGS_PATH = BASE / 'agents' / 'campaign-ops' / 'LEARNINGS.md'
REPORT_ROOT = BASE / 'reports' / 'agent'

TZ = ZoneInfo('Europe/Amsterdam')


@dataclass
class Finding:
    level: str  # OK/WARN/FAIL
    code: str
    message: str
    meta: dict[str, Any] | None = None


def now_local() -> datetime:
    return datetime.now(TZ)


def iso(ts: datetime) -> str:
    return ts.replace(microsecond=0).isoformat()


def ensure_state_fresh() -> None:
    rc = subprocess.run([sys.executable, str(FETCH_STATS)], cwd=str(BASE)).returncode
    if rc != 0:
        raise SystemExit(rc)


def http_check(url: str, expect_status: set[int] = {200}, method: str = 'GET', timeout: int = 20) -> tuple[bool, str]:
    req = urllib.request.Request(url, method=method, headers={'User-Agent': 'OpenClaw/CampaignOps/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = getattr(resp, 'status', 200)
            if status in expect_status:
                return True, f'HTTP {status}'
            return False, f'HTTP {status} (expected {sorted(expect_status)})'
    except urllib.error.HTTPError as e:
        if e.code in expect_status:
            return True, f'HTTP {e.code}'
        return False, f'HTTP {e.code} (expected {sorted(expect_status)})'
    except Exception as e:
        return False, f'ERR {e}'


def load_state() -> dict:
    return json.loads(STATE_PATH.read_text(encoding='utf-8'))


def db_connect() -> sqlite3.Connection:
    con = sqlite3.connect(str(DB_PATH))
    con.row_factory = sqlite3.Row
    return con


def db_scalar(con: sqlite3.Connection, q: str, args: tuple = ()) -> Any:
    cur = con.execute(q, args)
    row = cur.fetchone()
    return row[0] if row else None


def db_rows(con: sqlite3.Connection, q: str, args: tuple = ()) -> list[sqlite3.Row]:
    return list(con.execute(q, args))


def today_str() -> str:
    return now_local().date().isoformat()


def find_schedule_path() -> Path:
    return DAILY_ROOT / today_str() / 'schedule.json'


def compute_db_kpis(con: sqlite3.Connection) -> dict[str, Any]:
    # Overall
    total_leads = db_scalar(con, 'select count(*) from leads') or 0
    sent = db_scalar(con, "select count(*) from lead_campaigns where send_status='sent'") or 0
    delivered = db_scalar(con, "select count(*) from lead_campaigns where send_status='delivered'") or 0
    # Today
    today = today_str()
    sent_today = db_scalar(con, "select count(*) from lead_campaigns where sent_at like ?", (today + '%',)) or 0
    replies = db_scalar(con, "select count(*) from replies") or 0
    return {
        'total_leads': int(total_leads),
        'sent_total': int(sent),
        'delivered_total': int(delivered),
        'sent_today': int(sent_today),
        'replies_total': int(replies),
    }


def slot_counts_from_schedule(schedule: dict) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for b in schedule.get('batches', []) or []:
        key = str(b.get('batch') or '')
        if not key:
            continue
        out[key] = {
            'variant': b.get('variant'),
            'count_config': b.get('count_config'),
            'count_selected': b.get('count_selected'),
            'csv': b.get('csv'),
        }
    return out


def write_report(mode: str, status: str, checks: list[str], metrics: dict[str, Any], findings: list[Finding], proposals: list[str]) -> tuple[Path, Path]:
    ts = now_local()
    day_dir = REPORT_ROOT / today_str()
    day_dir.mkdir(parents=True, exist_ok=True)
    stamp = ts.strftime('%H%M')

    md_path = day_dir / f'{stamp}_{mode}.md'
    json_path = day_dir / f'{stamp}_{mode}.json'

    md = []
    md.append(f'# Campaign Ops Report — {today_str()} {ts.strftime("%H:%M")} ({mode})')
    md.append('')
    md.append(f'## Status: {status}')
    md.append('')
    md.append('## Wat ik heb gecheckt')
    for c in checks:
        md.append(f'- {c}')
    md.append('')
    md.append('## Belangrijkste metrics')
    for k, v in metrics.items():
        md.append(f'- {k}: {v}')
    md.append('')

    md.append('## Anomalies')
    if not findings:
        md.append('- (geen)')
    else:
        for f in findings:
            md.append(f'- [{f.level}] {f.code}: {f.message}')
    md.append('')

    md.append('## Voorstellen')
    if not proposals:
        md.append('- (geen)')
    else:
        for p in proposals[:3]:
            md.append(f'- {p}')
    md.append('')

    needs = [f for f in findings if f.level in ('FAIL', 'WARN')]
    md.append('## Actie nodig van Jean/Milan')
    if not needs:
        md.append('- Nee')
    else:
        md.append('- Jean: check anomalies en bepaal go/no-go of vervolgactie.')
    md.append('')

    md_path.write_text('\n'.join(md) + '\n', encoding='utf-8')
    json_payload = {
        'generated_at': iso(ts),
        'mode': mode,
        'status': status,
        'checks': checks,
        'metrics': metrics,
        'findings': [f.__dict__ for f in findings],
        'proposals': proposals[:3],
    }
    json_path.write_text(json.dumps(json_payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return md_path, json_path


def append_learning(findings: list[Finding], proposals: list[str]) -> None:
    if not any(f.level in ('FAIL', 'WARN') for f in findings):
        return
    ts = now_local().strftime('%Y-%m-%d %H:%M')
    lines = [f'\n## {ts}', '']
    for f in findings:
        if f.level in ('FAIL', 'WARN'):
            lines.append(f'- {f.level} {f.code}: {f.message}')
    if proposals:
        lines.append('- Proposal: ' + proposals[0])
    lines.append('')
    LEARNINGS_PATH.write_text(LEARNINGS_PATH.read_text(encoding='utf-8') + '\n'.join(lines), encoding='utf-8')


def mode_preflight() -> tuple[str, list[str], dict[str, Any], list[Finding], list[str]]:
    checks = ['Brevo API bereikbaarheid (fetch_brevo_stats)', 'Sender actief', 'CTA/asset URLs bereikbaar', 'Daily schedule aanwezig (indien enabled)']
    findings: list[Finding] = []
    proposals: list[str] = []

    ensure_state_fresh()
    state = load_state()

    sender = (state.get('brevo') or {}).get('configured_sender') or {}
    if not sender.get('found'):
        findings.append(Finding('FAIL', 'SENDER_NOT_FOUND', 'Configured sender_email niet gevonden in Brevo senders lijst.'))
    elif not sender.get('active'):
        findings.append(Finding('FAIL', 'SENDER_INACTIVE', 'Configured sender_email is niet actief in Brevo.'))

    # Asset checks (links komen uit config.local.json via send script, maar we checken live URLs hier expliciet)
    cfg = json.loads((BASE / 'config.local.json').read_text(encoding='utf-8'))
    aanvraag_url = (
        (cfg.get('brevo', {}) or {}).get('partner_aanvraag_api', {}) or {}
    ).get('url') or 'https://control.ecohandel.nl/partners/api/aanvraag.php'

    urls = {
        'eco_logo': cfg.get('brevo', {}).get('pricelist_logo_eco', ''),
        'deye_logo': cfg.get('brevo', {}).get('pricelist_logo_deye', ''),
        'pricelist': cfg.get('brevo', {}).get('pricelist_url', ''),
        'aanvraag_endpoint': str(aanvraag_url),
    }

    for label, url in urls.items():
        if not url:
            findings.append(Finding('WARN', 'URL_MISSING', f'Config mist URL voor {label}.'))
            continue
        expect = {200}
        method = 'GET'
        if label == 'aanvraag_endpoint':
            # endpoint bestaat als GET 405 geeft
            expect = {405, 200}
            method = 'GET'
        ok, detail = http_check(url, expect_status=expect, method=method)
        if not ok:
            findings.append(Finding('FAIL', 'URL_CHECK_FAILED', f'{label} check faalt: {detail} ({url})'))

    schedule_path = find_schedule_path()
    if not schedule_path.exists():
        findings.append(Finding('WARN', 'SCHEDULE_MISSING', f'Geen schedule.json gevonden voor vandaag ({schedule_path}).'))
        proposals.append('Laat prepare job eerder lopen (bijv. 08:45) of laat send-slot auto-prepare en log dit expliciet.')
    else:
        try:
            schedule = json.loads(schedule_path.read_text(encoding='utf-8'))
            low: list[str] = []
            for b in schedule.get('batches', []) or []:
                key = str(b.get('batch') or '')
                req = int(b.get('count_requested') or 0)
                sel = int(b.get('count_selected') or 0)
                if req and sel < req:
                    low.append(f'{key}: {sel}/{req}')
            if low:
                findings.append(Finding('FAIL', 'SCHEDULE_LOW_SELECTION', 'Te weinig unieke leads geselecteerd: ' + ', '.join(low)))
                proposals.append('Beslissing nodig: (A) vandaag B-slot met minder, (B) regels versoepelen (resend pool), of (C) extra leads importeren vóór 12:00.')
        except Exception as e:
            findings.append(Finding('FAIL', 'SCHEDULE_PARSE_FAILED', f'Kon schedule.json niet parsen: {e}'))

    metrics = {
        'brevo_ok': bool((state.get('brevo') or {}).get('brevo_ok')),
        'credits_remaining': (state.get('brevo') or {}).get('credits_remaining'),
        'sender_active': bool(sender.get('active')),
    }
    status = 'OK' if not any(f.level == 'FAIL' for f in findings) else 'FAIL'
    if status == 'OK' and any(f.level == 'WARN' for f in findings):
        status = 'WARN'
    return status, checks, metrics, findings, proposals


def mode_daily_summary() -> tuple[str, list[str], dict[str, Any], list[Finding], list[str]]:
    checks = ['Brevo stats refresh', 'DB KPI snapshot', 'Schedule vs DB consistency (licht)']
    findings: list[Finding] = []
    proposals: list[str] = []

    ensure_state_fresh()
    state = load_state()

    with db_connect() as con:
        kpi = compute_db_kpis(con)

        # Sanity: if we have sent_total but Brevo campaigns list is empty, flag.
        brevo_campaigns = len((state.get('brevo') or {}).get('campaigns') or [])
        if kpi.get('sent_total', 0) > 0 and brevo_campaigns == 0:
            findings.append(Finding('WARN', 'BREVO_CAMPAIGNS_EMPTY', 'DB toont sends, maar Brevo campaigns lijst is leeg in state (filtering/API?).'))
            proposals.append('Check fetch_brevo_stats filters/tagging zodat echte campagnes niet worden weggefilterd.')

        schedule_path = find_schedule_path()
        if schedule_path.exists():
            schedule = json.loads(schedule_path.read_text(encoding='utf-8'))
            slots = slot_counts_from_schedule(schedule)
            metrics = {
                **kpi,
                'schedule_slots': slots,
                'brevo_campaigns_seen': brevo_campaigns,
            }
        else:
            metrics = {
                **kpi,
                'brevo_campaigns_seen': brevo_campaigns,
            }

    status = 'OK' if not any(f.level == 'FAIL' for f in findings) else 'FAIL'
    if status == 'OK' and any(f.level == 'WARN' for f in findings):
        status = 'WARN'
    return status, checks, metrics, findings, proposals


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--mode', choices=['preflight', 'daily-summary'], default='daily-summary')
    args = p.parse_args()

    if args.mode == 'preflight':
        status, checks, metrics, findings, proposals = mode_preflight()
    else:
        status, checks, metrics, findings, proposals = mode_daily_summary()

    md_path, json_path = write_report(args.mode, status, checks, metrics, findings, proposals)
    append_learning(findings, proposals)

    print(str(md_path))
    print(str(json_path))

    # Exit code: only fail on FAIL.
    return 2 if status == 'FAIL' else 0


if __name__ == '__main__':
    raise SystemExit(main())
