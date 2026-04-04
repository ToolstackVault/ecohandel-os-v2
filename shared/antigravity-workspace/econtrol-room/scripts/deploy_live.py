#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/econtrol-room')
STATE_DIR = BASE / 'state'
DEPLOY_STATE_PATH = STATE_DIR / 'deploy-status.json'


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def main() -> None:
    payload = {
        'updated_at': utc_now(),
        'status': 'dry_run',
        'notes': 'Live deploy remains intentionally disabled in this script until explicit sync/deploy wiring is approved and configured.',
    }
    DEPLOY_STATE_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n')
    print(f'Wrote {DEPLOY_STATE_PATH}')


if __name__ == '__main__':
    main()
