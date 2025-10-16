#!/usr/bin/env bash
# defensive_stack/deploy_defense.sh
set -euo pipefail
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_DIR"
python3 -m venv venv || true
source venv/bin/activate
pip install --upgrade pip >/dev/null
# no heavy deps required; difflib is stdlib. If you want Levenshtein uncomment:
# pip install python-Levenshtein
mkdir -p logs quarantine
echo "Defense environment prepared."
echo "To test: python3 email_filter.py /path/to/email.eml"
