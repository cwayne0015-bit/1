"""
PrecisionOps Outreach Engine
Sends personalized cold emails to HVAC contractors. Claude writes the opener.

SETUP (one time, ~20 min):
1. pip install -r requirements.txt
2. Get Anthropic API key: console.anthropic.com → set ANTHROPIC_API_KEY env var
3. Gmail App Password: myaccount.google.com → Security → 2-Step → App Passwords
   Set GMAIL_USER and GMAIL_APP_PASSWORD env vars
4. Record ONE Loom demo of Estimate Builder (90 sec, generic) → paste URL below
5. Fill in YOUR_ADDRESS below (a real mailing address is legally required — see
   COMPLIANCE). A PO box is fine.
6. Build leads.csv (see GET_LEADS.txt)
7. Run: python outreach.py

COMPLIANCE (read this — it protects your domain and keeps you legal):
- US CAN-SPAM requires every commercial email to include (a) a working opt-out
  and (b) a valid physical postal address. Both are added automatically below.
- Anyone who replies "STOP" (or that you add to unsubscribed.csv) is skipped on
  every future run. Honor opt-outs within 10 business days — adding them to the
  file does that immediately.
- Already-emailed addresses (tracked in sent.csv) are skipped so you never
  double-send. Double-sending tanks deliverability and annoys prospects.

LIMITS:
- Gmail: ~500/day max before throttle. Start at 50/day, ramp up.
- For 1000+/day, swap send_email() to use Instantly or SendGrid.
"""

import csv
import os
import re
import smtplib
import time
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from anthropic import Anthropic

# ============ CONFIG ============
LOOM_DEMO_URL = "PASTE_YOUR_LOOM_URL_HERE"
YOUR_NAME = "Chris"
YOUR_BIZ = "Precision Construction"
YOUR_ADDRESS = "123 Main St, Suite 100, Your City, ST 00000"  # required by law
PRICE = "$297"
DAILY_LIMIT = 50
SEND_DELAY = 30  # seconds between sends
SENT_LOG = "sent.csv"
UNSUBSCRIBE_FILE = "unsubscribed.csv"
# ================================

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]


def _load_emails(path, column="email"):
    """Return a lowercased set of email addresses from a CSV column, if present."""
    seen = set()
    if not os.path.exists(path):
        return seen
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            addr = (row.get(column) or "").strip().lower()
            if addr:
                seen.add(addr)
    return seen


def load_suppression():
    """Emails we must not contact: already-sent + opted-out."""
    return _load_emails(SENT_LOG) | _load_emails(UNSUBSCRIBE_FILE)


def scrape_site_snippet(url):
    """Pull ~800 chars of readable text from contractor's homepage."""
    if not url:
        return ""
    try:
        if not url.startswith("http"):
            url = "https://" + url
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        text = r.text
        text = re.sub(r"<script.*?</script>", "", text, flags=re.DOTALL)
        text = re.sub(r"<style.*?</style>", "", text, flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:800]
    except Exception:
        return ""


def generate_opener(company, owner, city, snippet):
    """Claude writes 2-sentence personalized opener."""
    prompt = f"""Write a 2-sentence cold email opener for an HVAC contractor.

Contractor: {company}
Owner: {owner}
City: {city}
Website snippet: {snippet}

Rules:
- Sentence 1: reference something specific from their site or city (a service they offer, a neighborhood they serve, their years in business). Sound like a human actually looked.
- Sentence 2: bridge to a question about how long it currently takes them to send out estimates.
- No flattery. No "I love your website." No emojis.
- Under 40 words total.
- Output ONLY the 2 sentences. No preamble, no signature, no quotes."""

    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


def build_email(owner, company, opener):
    first_name = owner.split()[0] if owner else "there"
    return f"""Hey {first_name},

{opener}

Built a tool that turns a job description into a branded estimate PDF in about 10 seconds — your logo, your pricing, ready to send before the customer calls the next guy.

90-second demo: {LOOM_DEMO_URL}

{PRICE} to set it up on {company}'s system this week. Worth a quick look?

— {YOUR_NAME}
{YOUR_BIZ}
{YOUR_ADDRESS}

Not interested? Reply "STOP" and I won't email you again."""


def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg["From"] = f"{YOUR_NAME} <{GMAIL_USER}>"
    msg["To"] = to_email
    msg["Reply-To"] = GMAIL_USER
    msg["Subject"] = subject
    # One-click unsubscribe (RFC 8058 / 2369). Required for CAN-SPAM + helps
    # Gmail/Outlook surface a native "unsubscribe" button, protecting your sender rep.
    msg["List-Unsubscribe"] = f"<mailto:{GMAIL_USER}?subject=unsubscribe>"
    msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    msg.attach(MIMEText(body, "plain"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)


def main():
    with open("leads.csv", "r") as f:
        leads = list(csv.DictReader(f))

    suppress = load_suppression()
    log = []
    sent = 0
    skipped = 0

    for lead in leads:
        if sent >= DAILY_LIMIT:
            print(f"\nHit daily limit ({DAILY_LIMIT}). Stop.")
            break

        email = (lead.get("email") or "").strip()
        company = (lead.get("company") or "").strip()
        if not email or not company:
            continue

        if email.lower() in suppress:
            skipped += 1
            continue

        print(f"[{sent + 1}/{DAILY_LIMIT}] {company} → {email}")
        try:
            snippet = scrape_site_snippet(lead.get("website", ""))
            opener = generate_opener(
                company,
                lead.get("owner_name", ""),
                lead.get("city", ""),
                snippet,
            )
            body = build_email(lead.get("owner_name", ""), company, opener)
            subject = f"Quick demo for {company}"
            send_email(email, subject, body)
            log.append({**lead, "status": "sent", "opener": opener})
            suppress.add(email.lower())
            sent += 1
            print(f"   ✓ sent  |  opener: {opener[:60]}...")
            time.sleep(SEND_DELAY)
        except Exception as e:
            log.append({**lead, "status": f"failed: {e}", "opener": ""})
            print(f"   ✗ failed: {e}")

    if log:
        # Append so the sent log (and therefore de-dupe) persists across runs.
        new_file = not os.path.exists(SENT_LOG) or os.path.getsize(SENT_LOG) == 0
        with open(SENT_LOG, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=log[0].keys())
            if new_file:
                writer.writeheader()
            writer.writerows(log)

    print(f"\nDone. Sent {sent}, skipped {skipped} (already-sent or opted-out). Log: {SENT_LOG}")


if __name__ == "__main__":
    main()
