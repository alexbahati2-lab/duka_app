"""Smoke test for visitor DB and mailer utilities.

Run this script to verify that `init_visitor_db`, `save_visitor`, and
`get_recent_visitors` work and to optionally attempt sending an email
if email environment variables are configured.
"""

import os
import sys
from pathlib import Path
from pprint import pprint

# Ensure project root is on sys.path so `from utils...` works when running
# `python -u utils\\smoke_test.py` from the repository root.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.visitor_db import init_visitor_db, save_visitor, get_recent_visitors
from utils.whatsapp_notifier import notify


def main() -> None:
    print("Initializing visitor DB...")
    init_visitor_db()

    print("Saving a test visitor...")
    rowid = save_visitor("Test Visitor", "test@example.com")
    print(f"Inserted visitor row id: {rowid}")

    print("Recent visitors:")
    visitors = get_recent_visitors(5)
    pprint(visitors)

    # Email only if env vars are provided
    sender = os.environ.get("DUKA_EMAIL_SENDER")
    password = os.environ.get("DUKA_EMAIL_PASSWORD")
    receiver = os.environ.get("DUKA_EMAIL_RECEIVER")

    # Attempt WhatsApp send if Twilio env vars are provided
    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    token = os.environ.get("TWILIO_AUTH_TOKEN")
    whatsapp_from = os.environ.get("TWILIO_WHATSAPP_FROM")
    whatsapp_to = os.environ.get("TWILIO_WHATSAPP_TO")

    if sid and token and whatsapp_from and whatsapp_to:
        print("Attempting to send a test WhatsApp notification (using Twilio env vars)...")
        try:
            ok = notify("Test Visitor", "test@example.com")
            print("WhatsApp sent successfully." if ok else "WhatsApp failed to send.")
        except Exception as e:
            print(f"WhatsApp notifier raised an exception: {e}")
    else:
        print("Skipping WhatsApp send. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, TWILIO_WHATSAPP_TO to enable.")


if __name__ == "__main__":
    main()
