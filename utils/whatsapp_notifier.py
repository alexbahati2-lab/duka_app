"""WhatsApp notifier using Twilio.

Environment variables:
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_FROM` (e.g. 'whatsapp:+1415xxxx')
- `TWILIO_WHATSAPP_TO` (e.g. 'whatsapp:+2547xxxx')

Function: `notify(name: str, contact: str) -> bool`
"""

from __future__ import annotations

import os
from typing import Optional

from twilio.rest import Client


def _get_client() -> Client:
    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    token = os.environ.get("TWILIO_AUTH_TOKEN")
    if not sid or not token:
        raise RuntimeError("Twilio credentials not set in environment variables")
    return Client(sid, token)


def notify(name: str, contact: str, *, from_whatsapp: Optional[str] = None, to_whatsapp: Optional[str] = None) -> bool:
    """Send a WhatsApp message about a new visitor. Returns True on success."""
    client = _get_client()
    from_whatsapp = from_whatsapp or os.environ.get("TWILIO_WHATSAPP_FROM")
    to_whatsapp = to_whatsapp or os.environ.get("TWILIO_WHATSAPP_TO")
    if not from_whatsapp or not to_whatsapp:
        raise RuntimeError("Twilio WhatsApp phone numbers not configured (TWILIO_WHATSAPP_FROM/TO)")

    body = f"New Duka Demo Visitor:\nName: {name}\nContact: {contact or 'N/A'}"

    try:
        message = client.messages.create(body=body, from_=from_whatsapp, to=to_whatsapp)
        return bool(message.sid)
    except Exception:
        return False


__all__ = ["notify"]
