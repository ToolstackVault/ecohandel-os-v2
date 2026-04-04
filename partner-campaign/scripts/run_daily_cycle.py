#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/partner-campaign/scripts')
STEPS = [
    'sync_brevo_events.py',
    'ingest_partner_requests.py',
    'ingest_partner_clicks.py',
    'recalculate_scores.py',
    'classify_replies.py',
    'report_hot_prospects.py',
]


def main() -> int:
    for step in STEPS:
        path = BASE / step
        print(f'▶ Running {step}')
        rc = subprocess.run([sys.executable, str(path)]).returncode
        if rc != 0:
            return rc
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
