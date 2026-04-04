#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/econtrol-room')
RENDER = BASE / 'render_econtrol_room.py'


def main() -> int:
    if not RENDER.exists():
        print(f'Missing renderer: {RENDER}', file=sys.stderr)
        return 1
    return subprocess.call([sys.executable, str(RENDER)])


if __name__ == '__main__':
    raise SystemExit(main())
