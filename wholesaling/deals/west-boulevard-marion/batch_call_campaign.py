"""
Outbound batch campaign runner — ElevenLabs Conversational AI.

One property per campaign. Buyers only. Tier A/B numbers only.

Env:
  ELEVENLABS_API_KEY
  ELEVENLABS_AGENT_ID          agent_8701ky1adxzxf8cacq28h8pba1fv
  ELEVENLABS_PHONE_NUMBER_ID   from the imported Twilio number
"""

import os
import csv
import sys
import time
import json
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

API = "https://api.elevenlabs.io/v1/convai/batch-calling"
KEY = os.environ["ELEVENLABS_API_KEY"]
AGENT_ID = os.environ["ELEVENLABS_AGENT_ID"]
PHONE_ID = os.environ["ELEVENLABS_PHONE_NUMBER_ID"]
TZ = ZoneInfo("America/Chicago")

HEADERS = {"xi-api-key": KEY, "Content-Type": "application/json"}

# ---------------------------------------------------------------- property

PROPERTY = {
    "property_city":   "Marion",
    "property_street": "West Boulevard",
    "beds":            "3",
    "baths":           "1",
    "sqft":            "1150",
    "year_built":      "1962",
    "repair_scope":    "full bath, kitchen, roof, and HVAC",
    "arv_range":       "one thirty-five to one forty-five",
    "ask_price":       "seventy-two thousand",
    "days_to_close":   "14",
}

# ---------------------------------------------------------------- gating

ALLOWED_LINE_TYPES = {"landline", "voip_business"}   # Tier A
CONSENTED = {"yes", "true", "1"}                      # Tier B


def load_recipients(path):
    """
    CSV columns:
      phone_number,buyer_name,buyer_company,line_type,consent_on_file,dnc,last_called
    """
    keep, dropped = [], []
    cutoff = datetime.now(TZ) - timedelta(hours=48)

    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            phone = row["phone_number"].strip()

            if row.get("dnc", "").strip().lower() in CONSENTED:
                dropped.append((phone, "dnc")); continue

            line_ok = row.get("line_type", "").strip().lower() in ALLOWED_LINE_TYPES
            consent_ok = row.get("consent_on_file", "").strip().lower() in CONSENTED
            if not (line_ok or consent_ok):
                dropped.append((phone, "tier_c_no_consent")); continue

            last = row.get("last_called", "").strip()
            if last:
                try:
                    if datetime.fromisoformat(last).astimezone(TZ) > cutoff:
                        dropped.append((phone, "cooldown")); continue
                except ValueError:
                    pass

            keep.append({
                "phone_number": phone,
                "conversation_initiation_client_data": {
                    "dynamic_variables": {
                        "buyer_name": row.get("buyer_name", "there").strip(),
                        "buyer_company": row.get("buyer_company", "").strip(),
                        **PROPERTY,
                    }
                },
            })

    return keep, dropped


def next_window(hour=10):
    """Next weekday slot at `hour` local. Never nights, never weekends."""
    t = datetime.now(TZ)
    target = t.replace(hour=hour, minute=0, second=0, microsecond=0)
    if target <= t:
        target += timedelta(days=1)
    while target.weekday() >= 5:          # Sat/Sun
        target += timedelta(days=1)
    return int(target.timestamp())


# ---------------------------------------------------------------- submit

def submit(name, recipients, concurrency=5, schedule=True):
    payload = {
        "call_name": name,
        "agent_id": AGENT_ID,
        "agent_phone_number_id": PHONE_ID,
        "recipients": recipients,
        "timezone": "America/Chicago",
        "target_concurrency_limit": concurrency,
        "telephony_call_config": {"ringing_timeout_secs": 25},
    }
    if schedule:
        payload["scheduled_time_unix"] = next_window()

    r = requests.post(f"{API}/submit", headers=HEADERS, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()


def watch(batch_id, interval=30):
    while True:
        r = requests.get(f"{API}/{batch_id}", headers=HEADERS, timeout=30)
        r.raise_for_status()
        b = r.json()
        print(f"{b['status']:12} "
              f"dispatched={b['total_calls_dispatched']} "
              f"finished={b['total_calls_finished']}/{b['total_calls_scheduled']}")
        if b["status"] in ("completed", "failed", "cancelled"):
            return b
        time.sleep(interval)


def cancel(batch_id):
    r = requests.post(f"{API}/{batch_id}/cancel", headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------- main

if __name__ == "__main__":
    csv_path = sys.argv[1]
    recipients, dropped = load_recipients(csv_path)

    print(f"eligible: {len(recipients)}   dropped: {len(dropped)}")
    for phone, reason in dropped[:20]:
        print(f"  drop {phone}  {reason}")

    if not recipients:
        sys.exit("nothing eligible")

    # First run: cap at 25 so you can listen before scaling.
    if len(recipients) > 25:
        print(f"capping first batch at 25 (of {len(recipients)})")
        recipients = recipients[:25]

    if input(f"submit {len(recipients)} calls? [y/N] ").lower() != "y":
        sys.exit("aborted")

    batch = submit(
        name=f"{PROPERTY['property_street']} — buyers — {datetime.now(TZ):%m/%d}",
        recipients=recipients,
    )
    print(json.dumps(batch, indent=2))
    watch(batch["id"])
