"""Compatibility wrapper exposing `notify` from `whatsapp_notifier`.

This module keeps the old import path `utils.mailer.notify` working while
the implementation lives in `utils.whatsapp_notifier`.
"""

from .whatsapp_notifier import notify

__all__ = ["notify"]

