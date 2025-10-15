#!/usr/bin/env python3
import sys, os, time
from email.message import EmailMessage

REPO_DIR = os.path.dirname(__file__)
ART = os.path.join(REPO_DIR, 'artifacts')
os.makedirs(ART, exist_ok=True)

recipient = sys.argv[1] if len(sys.argv) > 1 else 'testuser@local.lab'

# SAFEGUARD: recipient whitelist
with open(os.path.join(REPO_DIR, 'recipient_whitelist.txt')) as f:
    allowed = [l.strip() for l in f if l.strip()]
if recipient not in allowed:
    print("SAFEGUARD: Recipient not whitelisted. Aborting.")
    sys.exit(1)

msg = EmailMessage()
msg['From'] = 'IT Support <it-support@example.com>'
msg['To'] = recipient
msg['Subject'] = 'Action required: Confirm your account'
msg.set_content('Please confirm your account: http://127.0.0.1:8000/phish')

fn = os.path.join(ART, f"email-{int(time.time())}.eml")
with open(fn, 'w') as f:
    f.write(msg.as_string())
print(f"Generated email: {fn}")
