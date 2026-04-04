#!/bin/bash
set -euo pipefail
CRON_FILE="/Users/ecohandel.nl/.openclaw/workspace/ecohandel/econtrol-room/cron/econtrol-room-v1.cron"
TMP_FILE="/tmp/econtrol-room-crontab.txt"

crontab -l 2>/dev/null | grep -v 'econtrol-room/scripts/ops_cycle.py' > "$TMP_FILE" || true
cat "$CRON_FILE" >> "$TMP_FILE"
crontab "$TMP_FILE"
echo "Installed Econtrol Room crontab from $CRON_FILE"
