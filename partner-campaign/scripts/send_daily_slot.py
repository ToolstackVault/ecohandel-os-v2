#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/partner-campaign')
CONFIG_PATH = BASE / 'daily_send_config.json'
DAILY_ROOT = BASE / 'launch' / 'daily'
PREPARE_SCRIPT = BASE / 'scripts' / 'prepare_daily_batches.py'
SEND_SCRIPT = BASE / 'scripts' / 'send_batch_campaign.py'
RUN_DAILY_CYCLE = BASE / 'scripts' / 'run_daily_cycle.py'
FETCH_STATS = BASE / 'scripts' / 'fetch_brevo_stats.py'


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding='utf-8'))


def today_dir(cfg: dict) -> Path:
    tz = ZoneInfo(cfg.get('timezone', 'Europe/Amsterdam'))
    today = datetime.now(tz).date().isoformat()
    return DAILY_ROOT / today


def ensure_prepared(cfg: dict) -> Path:
    out_dir = today_dir(cfg)
    schedule_path = out_dir / 'schedule.json'
    if not schedule_path.exists():
        rc = subprocess.run([sys.executable, str(PREPARE_SCRIPT)]).returncode
        if rc != 0:
            raise SystemExit(rc)
    return schedule_path


def main() -> int:
    parser = argparse.ArgumentParser(description='Send one configured EcoHandel daily slot')
    parser.add_argument('slot_key', help='Configured daily slot key, e.g. A0900 or B1200')
    parser.add_argument('--test-email', help='Override recipients to a single test email')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    cfg = load_config()
    if not cfg.get('enabled', True):
        raise SystemExit('Daily partner campaign sending is disabled in daily_send_config.json')

    schedule_path = ensure_prepared(cfg)
    schedule = json.loads(schedule_path.read_text(encoding='utf-8'))
    batch = next((b for b in schedule.get('batches', []) if b.get('batch') == args.slot_key), None)
    if not batch:
        raise SystemExit(f'Slot {args.slot_key} not found in {schedule_path}')
    if int(batch.get('count_selected', 0)) <= 0:
        raise SystemExit(f'Slot {args.slot_key} has 0 selected leads; nothing will be sent')

    cmd = [sys.executable, str(SEND_SCRIPT), args.slot_key, '--schedule-file', str(schedule_path)]
    if args.dry_run:
        cmd.append('--dry-run')
    if args.test_email:
        cmd.extend(['--test-email', args.test_email])

    rc = subprocess.run(cmd).returncode
    if rc != 0:
        return rc
    if not args.dry_run:
        for follow_up in (RUN_DAILY_CYCLE, FETCH_STATS):
            rc = subprocess.run([sys.executable, str(follow_up)]).returncode
            if rc != 0:
                return rc
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
