#!/usr/bin/env python3
from pathlib import Path
import shutil
import subprocess
import sys

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/econtrol-room')
RENDER = BASE / 'render_econtrol_room.py'
BUILD = BASE / 'build'
INDEX = BUILD / 'index.html'
DASHBOARD = BUILD / 'dashboard.html'


def main() -> int:
    if not RENDER.exists():
        print(f'Missing renderer: {RENDER}', file=sys.stderr)
        return 1
    code = subprocess.call([sys.executable, str(RENDER)])
    if code != 0:
        return code
    if INDEX.exists():
        shutil.copyfile(INDEX, DASHBOARD)
        print(f'Synced {DASHBOARD} from {INDEX}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
