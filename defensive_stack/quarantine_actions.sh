#!/usr/bin/env bash
# defensive_stack/quarantine_actions.sh
set -euo pipefail
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
LOGS="$REPO_DIR/logs"
QUAR="$REPO_DIR/quarantine"
mkdir -p "$LOGS" "$QUAR"
EML="$1"
REASON="${2:-quarantined}"
if [ ! -f "$EML" ]; then
  echo "Usage: $0 path/to/email.eml [reason]"
  exit 1
fi
cp "$EML" "$QUAR/"
echo "$(date --iso-8601=seconds) | $REASON | $(basename "$EML")" >> "$LOGS/alerts.log"
echo "Quarantined: $(basename "$EML")"
