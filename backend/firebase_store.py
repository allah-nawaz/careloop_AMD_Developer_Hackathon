"""
firebase_store.py
Optional Realtime Database storage for CareLoop journal entries.

How this fits into the app:
- If a Firebase service account key and database URL are configured,
  entries are saved to and read from Firebase Realtime Database (a real
  cloud database).
- If that's not set up, main.py falls back to the local entries.json file
  instead - so the app still works with zero Firebase setup, same idea as
  the AI scoring fallback in scorer.py.

This uses Realtime Database rather than Firestore because Firestore
requires a billing account to be linked, even for free-tier usage.
Realtime Database does not have that requirement.
"""

import os

import firebase_admin
from firebase_admin import credentials, db

_initialized = False
_tried_and_failed = False


def _ensure_initialized() -> bool:
    """
    Sets up the connection to Firebase once, and remembers whether it
    worked so we don't retry a broken connection on every request.
    """
    global _initialized, _tried_and_failed

    if _initialized:
        return True
    if _tried_and_failed:
        return False

    cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH", "").strip()
    database_url = os.environ.get("FIREBASE_DATABASE_URL", "").strip()

    if not cred_path or not os.path.exists(cred_path) or not database_url:
        _tried_and_failed = True
        return False

    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {"databaseURL": database_url})
        _initialized = True
        return True
    except Exception:
        _tried_and_failed = True
        return False


def save_entry_firestore(entry: dict) -> bool:
    """Save one journal entry to Firebase. Returns True on success."""
    if not _ensure_initialized():
        return False
    try:
        db.reference("journal_entries").push(entry)
        return True
    except Exception:
        return False


def load_entries_firestore():
    """
    Load all journal entries from Firebase, oldest first.
    Returns None (not an empty list) if Firebase isn't configured or
    reachable, so main.py knows to fall back to the local file instead.
    """
    if not _ensure_initialized():
        return None
    try:
        data = db.reference("journal_entries").get()
        if not data:
            return []
        entries = list(data.values())
        entries.sort(key=lambda e: e.get("timestamp", ""))
        return entries
    except Exception:
        return None
