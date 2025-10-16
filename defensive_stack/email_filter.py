#!/usr/bin/env python3
# defensive_stack/email_filter.py
import sys, re, os, shutil, json
from email import message_from_file
from domain_similarity_detector import is_similar

REPO = os.path.dirname(__file__)
LOGS = os.path.join(REPO, 'logs')
QUAR = os.path.join(REPO, 'quarantine')
os.makedirs(LOGS, exist_ok=True)
os.makedirs(QUAR, exist_ok=True)

# Configure your canonical/known-good domains here
CANONICAL_DOMAINS = ["example.com", "university.edu"]

# thresholds
SIMILARITY_THRESHOLD = 0.85
PHISH_SCORE_THRESHOLD = 7
SUSPICIOUS_SCORE_THRESHOLD = 4

def extract_urls(text):
    return re.findall(r'https?://[^\s\'"<>]+', text or "")

def score_email(eml_path):
    m = message_from_file(open(eml_path))
    # body may be plain or multipart; attempt to get a text payload
    body = ""
    try:
        body = m.get_payload(decode=True).decode('utf-8', errors='ignore') if m.is_multipart() else (m.get_payload() or "")
    except Exception:
        body = m.get_payload() or ""
    subject = m.get('Subject', '')
    from_hdr = m.get('From', '')
    # extract sender address
    from email.utils import parseaddr
    sender_addr = parseaddr(from_hdr)[1]
    sender_domain = sender_addr.split('@')[-1] if '@' in sender_addr else ''

    score = 0
    evidence = []

    # URL check
    urls = extract_urls(body)
    for u in urls:
        # mark external (not local lab IPs)
        if not ("127.0.0.1" in u or u.startswith("http://10.") or "localhost" in u):
            score += 5
            evidence.append(f"external_url:{u}")

    # domain similarity check
    if sender_domain:
        sim, sc, canon = is_similar(sender_domain, CANONICAL_DOMAINS, SIMILARITY_THRESHOLD)
        if sim:
            score += 4
            evidence.append(f"domain_sim:{sender_domain}->{canon}:{sc:.2f}")

    # subject heuristics
    if re.search(r'\b(urgent|action required|confirm now|verify|password)\b', subject, re.I):
        score += 1
        evidence.append("subject_urgency")

    # mismatch display name vs address (simple heuristic)
    display_name = from_hdr.split('<')[0].strip().strip('"')
    if display_name and '@' not in display_name and display_name and sender_domain:
        # if display name contains canonical org name but sender domain is different, mark it
        for c in CANONICAL_DOMAINS:
            if c.split('.')[0].lower() in display_name.lower() and c not in sender_domain.lower():
                score += 2
                evidence.append("displayname_mismatch")

    return score, evidence, sender_addr, subject

def quarantine(eml_path, reason):
    base = os.path.basename(eml_path)
    dst = os.path.join(QUAR, base)
    shutil.copy2(eml_path, dst)
    with open(os.path.join(LOGS, 'alerts.log'), 'a') as f:
        f.write(f"{reason} | {base}\n")
    return dst

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: email_filter.py path/to/email.eml")
        sys.exit(1)
    eml = sys.argv[1]
    score, evidence, sender, subject = score_email(eml)
    print(f"Score: {score} Evidence: {evidence}")
    if score >= PHISH_SCORE_THRESHOLD:
        print("PHISHING detected - quarantining email")
        q = quarantine(eml, f"score={score} evidence={evidence}")
        print("Quarantined to:", q)
    elif score >= SUSPICIOUS_SCORE_THRESHOLD:
        print("SUSPICIOUS - logging for review")
        with open(os.path.join(LOGS, 'filter.log'),'a') as f:
            f.write(f"suspicious | {os.path.basename(eml)} | score={score} | evidence={evidence}\n")
    else:
        print("LOW RISK / SAFE")
