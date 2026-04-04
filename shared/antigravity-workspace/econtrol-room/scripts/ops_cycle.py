#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/econtrol-room')
STATE_DIR = BASE / 'state'
OPS_STATUS_PATH = STATE_DIR / 'ops-status.json'

STEP_COMMANDS = [
    ('refresh_sources', [sys.executable, str(BASE / 'scripts' / 'refresh_sources.py')]),
    ('score_queue', [sys.executable, str(BASE / 'scripts' / 'score_queue.py')]),
    ('update_state', [sys.executable, str(BASE / 'scripts' / 'update_state.py')]),
    ('render_dashboard', [sys.executable, str(BASE / 'scripts' / 'render_dashboard.py')]),
    ('render_queue_page', [sys.executable, str(BASE / 'scripts' / 'render_queue_page.py')]),
    ('trigger_specialists', [sys.executable, str(BASE / 'scripts' / 'trigger_specialists.py')]),
    ('generate_workflow_state', [sys.executable, str(BASE / 'scripts' / 'generate_workflow_state.py')]),
    ('render_workflows_page', [sys.executable, str(BASE / 'scripts' / 'render_workflows_page.py')]),
    ('render_partner_campaign_page', [sys.executable, str(BASE / 'scripts' / 'render_partner_campaign_page.py')]),
    ('render_pwa_assets', [sys.executable, str(BASE / 'scripts' / 'render_pwa_assets.py')]),
    ('deploy_live', [sys.executable, str(BASE / 'scripts' / 'deploy_live.py')]),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def main() -> None:
    now = utc_now()
    completed_steps: list[str] = []
    failed_steps: list[str] = []
    step_logs: list[dict] = []

    for step_name, command in STEP_COMMANDS:
        proc = subprocess.run(command, capture_output=True, text=True)
        ok = proc.returncode == 0
        step_logs.append({
            'step': step_name,
            'ok': ok,
            'returncode': proc.returncode,
            'stdout': proc.stdout.strip(),
            'stderr': proc.stderr.strip(),
        })
        if ok:
            completed_steps.append(step_name)
        else:
            failed_steps.append(step_name)
            break

    status = {
        'updated_at': utc_now(),
        'ops_status': 'ok' if not failed_steps else 'degraded',
        'mode': 'active',
        'last_run': now,
        'last_successful_step': completed_steps[-1] if completed_steps else None,
        'last_failed_step': failed_steps[-1] if failed_steps else None,
        'completed_steps': completed_steps,
        'failed_steps': failed_steps,
        'pending_actions': [
            'Connect live external source pulls for GSC/Ads/Shopify.',
            'Wire deploy_live.py to approved sync flow when ready.',
            'Add specialist-agent trigger execution paths.',
        ],
        'warnings': [
            'Deploy remains dry-run by design until explicit live-sync approval/wiring exists.',
        ] if not failed_steps else [
            'Ops cycle stopped before finishing all steps.',
        ],
        'usage_notes': 'Deterministic scripts handled the cycle; no specialist agents were invoked.',
        'planned_steps': [step for step, _ in STEP_COMMANDS],
        'step_logs': step_logs,
    }
    write_json(OPS_STATUS_PATH, status)
    print(f'Wrote {OPS_STATUS_PATH}')


if __name__ == '__main__':
    main()
