#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/econtrol-room')
STATE_PATH = BASE / 'state' / 'publish-status.json'
PUBLISH_CONFIG_PATH = BASE / 'sources' / 'publish-system.json'
DEFAULT_PUBLISH_SCRIPT = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/content-system/kennisblog/publish_article.py')


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def write_state(data: dict) -> None:
    STATE_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def load_publish_config() -> dict:
    if PUBLISH_CONFIG_PATH.exists():
        return json.loads(PUBLISH_CONFIG_PATH.read_text())
    return {}


def main() -> int:
    parser = argparse.ArgumentParser(description='Controlled EcoHandel Shopify publish wrapper')
    parser.add_argument('html_file', help='HTML file to validate/publish')
    parser.add_argument('--title', required=True)
    parser.add_argument('--author', default='Milan')
    parser.add_argument('--tags', default='deye')
    parser.add_argument('--excerpt')
    parser.add_argument('--update', type=int)
    parser.add_argument('--approve', action='store_true', help='Required for non-dry-run publish')
    parser.add_argument('--dry-run', action='store_true', help='Validate only')
    args = parser.parse_args()

    publish_config = load_publish_config()
    publish_script = Path(publish_config.get('paths', {}).get('publisher', DEFAULT_PUBLISH_SCRIPT))
    playbook_path = publish_config.get('paths', {}).get('playbook', 'ecohandel/content-system/kennisblog/PUBLISH_PLAYBOOK.md')
    template_path = publish_config.get('paths', {}).get('template', 'ecohandel/content-system/kennisblog/TEMPLATE.html')

    state = {
        'updated_at': utc_now(),
        'status': 'blocked',
        'store': 'ecohandel-shopify',
        'channel': 'shopify',
        'script': str(publish_script),
        'playbook': playbook_path,
        'template': template_path,
        'notes': 'Publish is approval-gated by design and linked to the Econtrol Room content system.',
    }

    if not publish_script.exists():
        state['status'] = 'error'
        state['notes'] = 'Underlying Shopify publish script not found.'
        write_state(state)
        print('Missing publish script', file=sys.stderr)
        return 1

    cmd = [sys.executable, str(publish_script), args.html_file, '--title', args.title, '--author', args.author, '--tags', args.tags]
    if args.excerpt:
        cmd += ['--excerpt', args.excerpt]
    if args.update:
        cmd += ['--update', str(args.update)]

    if args.dry_run or not args.approve:
        cmd += ['--dry-run']
        state['status'] = 'dry_run'
        state['notes'] = 'Validation only. Add --approve for live publish.'
    else:
        state['status'] = 'publishing'
        state['notes'] = 'Approved live publish invoked.'

    write_state(state)
    result = subprocess.run(cmd)

    final = {
        'updated_at': utc_now(),
        'status': 'ok' if result.returncode == 0 else 'error',
        'store': 'ecohandel-shopify',
        'channel': 'shopify',
        'script': str(publish_script),
        'playbook': playbook_path,
        'template': template_path,
        'last_command': cmd,
        'notes': 'Publish wrapper finished.' if result.returncode == 0 else 'Publish wrapper failed.',
    }
    write_state(final)
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
