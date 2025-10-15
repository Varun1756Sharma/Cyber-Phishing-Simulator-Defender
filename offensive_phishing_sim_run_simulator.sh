#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
ARTIFACTS="$REPO_DIR/artifacts"
mkdir -p "$ARTIFACTS"

# SAFEGUARDS
if [ -z "${LAB_TOKEN:-}" ]; then
  echo "SAFEGUARD: LAB_TOKEN missing. Aborting."
  exit 1
fi

WHITELIST_JSON="$REPO_DIR/whitelist.json"
if [ ! -f "$WHITELIST_JSON" ]; then
  echo "SAFEGUARD: whitelist.json missing. Aborting."
  exit 1
fi

HOSTNAME="$(hostname)"
if ! grep -q "\"$HOSTNAME\"" "$WHITELIST_JSON"; then
  echo "SAFEGUARD: Hostname '$HOSTNAME' not in whitelist.json. Aborting."
  exit 1
fi

RECIP="${1:-}"
if [ -z "$RECIP" ]; then
  echo "Usage: $0 recipient@example.lab"
  exit 1
fi

RECIP_LIST="$REPO_DIR/recipient_whitelist.txt"
if [ ! -f "$RECIP_LIST" ]; then
  echo "SAFEGUARD: recipient_whitelist.txt missing. Aborting."
  exit 1
fi
if ! grep -Fxq "$RECIP" "$RECIP_LIST"; then
  echo "SAFEGUARD: Recipient $RECIP not whitelisted. Aborting."
  exit 1
fi

# SMTP check (MailHog)
SMTP_HOST="127.0.0.1"
SMTP_PORT=1025
if ! nc -z "$SMTP_HOST" "$SMTP_PORT" >/dev/null 2>&1; then
  echo "SAFEGUARD: SMTP $SMTP_HOST:$SMTP_PORT not reachable. Aborting."
  exit 1
fi

# startup audit
STARTUP_FILE="$ARTIFACTS/startup_$(date +%s).log"
{
  echo "startup_time: $(date --iso-8601=seconds)"
  echo "hostname: $HOSTNAME"
  echo "recipient: $RECIP"
} > "$STARTUP_FILE"
echo "SAFEGUARD: startup audit written to $STARTUP_FILE"

# generate and send email
EML_FILE="${2:-}"
if [ -z "$EML_FILE" ]; then
  python3 "$REPO_DIR/generate_email.py" "$RECIP"
  EML_FILE="$(ls -t "$ARTIFACTS"/email-*.eml | head -n1)"
fi

python3 - <<PY
import smtplib
from email import message_from_file
m = message_from_file(open("$EML_FILE"))
s = smtplib.SMTP("$SMTP_HOST", $SMTP_PORT, timeout=10)
s.sendmail(m['From'], [m['To']], m.as_string())
s.quit()
print("Email sent to $RECIP (local only).")
PY
