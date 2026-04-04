#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/econtrol-room')
SCRIPTS = {
    'source_refresh': BASE / 'scripts' / 'refresh_sources.py',
    'queue_scoring': BASE / 'scripts' / 'score_queue.py',
    'state_update': BASE / 'scripts' / 'update_state.py',
    'dashboard_render': BASE / 'scripts' / 'render_dashboard.py',
    'queue_render': BASE / 'scripts' / 'render_queue_page.py',
    'specialist_trigger_generation': BASE / 'scripts' / 'trigger_specialists.py',
    'workflow_state_build': BASE / 'scripts' / 'generate_workflow_state.py',
    'workflow_render': BASE / 'scripts' / 'render_workflows_page.py',
    'partner_campaign_render': BASE / 'scripts' / 'render_partner_campaign_page.py',
    'deploy_sync': BASE / 'scripts' / 'deploy_live.py',
}

FLOWS = {
    'refresh_stack': ['source_refresh', 'queue_scoring', 'state_update'],
    'render_stack': ['dashboard_render', 'queue_render', 'workflow_render', 'partner_campaign_render'],
    'workflow_stack': ['workflow_state_build', 'workflow_render'],
    'full_non_deploy': ['source_refresh', 'queue_scoring', 'state_update', 'dashboard_render', 'queue_render', 'specialist_trigger_generation', 'workflow_state_build', 'workflow_render', 'partner_campaign_render'],
}


def run_script(path: Path) -> int:
    if not path.exists():
        print(f'Missing script: {path}', file=sys.stderr)
        return 1
    print(f'▶ Running {path.name}')
    proc = subprocess.run([sys.executable, str(path)])
    return proc.returncode


def run_sequence(items: list[str]) -> int:
    for item in items:
        script = SCRIPTS.get(item)
        if not script:
            print(f'Unknown workflow: {item}', file=sys.stderr)
            return 1
        rc = run_script(script)
        if rc != 0:
            return rc
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Run one workflow or a predefined stack for Econtrol Room.')
    parser.add_argument('target', help='Workflow id or stack alias')
    args = parser.parse_args()

    if args.target in FLOWS:
        return run_sequence(FLOWS[args.target])
    return run_sequence([args.target])


if __name__ == '__main__':
    raise SystemExit(main())
