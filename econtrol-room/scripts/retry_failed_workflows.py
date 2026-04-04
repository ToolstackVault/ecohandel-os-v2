#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/econtrol-room')
OPS_STATUS_PATH = BASE / 'state' / 'ops-status.json'
RUN_WORKFLOW = BASE / 'scripts' / 'run_workflow.py'
STEP_TO_WORKFLOW = {
    'refresh_sources': 'source_refresh',
    'score_queue': 'queue_scoring',
    'update_state': 'state_update',
    'render_dashboard': 'dashboard_render',
    'render_queue_page': 'queue_render',
    'trigger_specialists': 'specialist_trigger_generation',
    'generate_workflow_state': 'workflow_state_build',
    'render_workflows_page': 'workflow_render',
    'deploy_live': 'deploy_sync',
}


def main() -> int:
    if not OPS_STATUS_PATH.exists():
        print('No ops-status.json found.', file=sys.stderr)
        return 1
    ops = json.loads(OPS_STATUS_PATH.read_text())
    failed = ops.get('failed_steps', [])
    if not failed:
        print('No failed steps to retry.')
        return 0
    targets = []
    for step in failed:
        target = STEP_TO_WORKFLOW.get(step)
        if target:
            targets.append(target)
    if not targets:
        print('Failed steps found, but no mapped workflow ids.', file=sys.stderr)
        return 1
    rc = 0
    for target in targets:
        print(f'↻ Retrying {target}')
        proc = subprocess.run([sys.executable, str(RUN_WORKFLOW), target])
        if proc.returncode != 0:
            rc = proc.returncode
            break
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
