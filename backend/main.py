"""
main.py
CareLoop backend
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from scorer import (
    CATEGORIES,
    keyword_score,
    build_ai_prompt,
    overall_from_ai,
)

from firebase_store import (
    save_entry_firestore,
    load_entries_firestore,
)

# ---------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------

app = FastAPI(title="CareLoop API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

ENTRIES_FILE = DATA_DIR / "entries.json"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

FIREWORKS_API_KEY = os.environ.get(
    "FIREWORKS_API_KEY", ""
).strip()

FIREWORKS_MODEL = os.environ.get(
    "FIREWORKS_MODEL",
    "accounts/fireworks/models/gemma3-27b-it",
)


class JournalEntry(BaseModel):
    text: str


# ---------------------------------------------------------------------
# Storage helpers
# ---------------------------------------------------------------------

def _load_local_entries():
    if not ENTRIES_FILE.exists():
        return []

    with open(ENTRIES_FILE, "r") as f:
        return json.load(f)


def _save_local_entry(entry: dict):
    entries = _load_local_entries()
    entries.append(entry)

    with open(ENTRIES_FILE, "w") as f:
        json.dump(entries, f, indent=2)


def load_entries():
    firestore_entries = load_entries_firestore()

    if firestore_entries is not None:
        return firestore_entries

    return _load_local_entries()


def save_entry(entry: dict):
    if save_entry_firestore(entry):
        return

    _save_local_entry(entry)


# ---------------------------------------------------------------------
# Gemini AI
# ---------------------------------------------------------------------

def score_with_gemini(journal_text: str):

    if not GEMINI_API_KEY:
        return None

    try:

        prompt = build_ai_prompt(journal_text)

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            "gemini-2.5-flash:generateContent"
        )

        response = requests.post(
            url,
            headers={
                "x-goog-api-key": GEMINI_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            },
            timeout=20,
        )

        response.raise_for_status()

        raw_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]

        raw_text = (
            raw_text.strip()
            .strip("`")
            .replace("json\n", "", 1)
        )

        parsed = json.loads(raw_text)

        scores = {
            category: parsed.get(category, 0)
            for category in CATEGORIES
        }

        return {
            "scores": scores,
            "overall": overall_from_ai(scores),
            "summary": parsed.get("summary", ""),
            "source": "gemini",
        }

    except Exception as e:
        print(f"[CareLoop] Gemini failed: {e}")
        return None


# ---------------------------------------------------------------------
# Fireworks AI
# ---------------------------------------------------------------------

def score_with_fireworks(journal_text: str):

    if not FIREWORKS_API_KEY:
        return None

    try:

        prompt = build_ai_prompt(journal_text)

        response = requests.post(
            "https://api.fireworks.ai/inference/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {FIREWORKS_API_KEY}"
            },
            json={
                "model": FIREWORKS_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "max_tokens": 300,
            },
            timeout=20,
        )

        response.raise_for_status()

        raw_text = response.json()["choices"][0]["message"]["content"]

        raw_text = (
            raw_text.strip()
            .strip("`")
            .replace("json\n", "", 1)
        )

        parsed = json.loads(raw_text)

        scores = {
            category: parsed.get(category, 0)
            for category in CATEGORIES
        }

        return {
            "scores": scores,
            "overall": overall_from_ai(scores),
            "summary": parsed.get("summary", ""),
            "source": "fireworks",
        }

    except Exception as e:
        print(f"[CareLoop] Fireworks failed: {e}")
        return None
    
    # ---------------------------------------------------------------------
# Score selection
# ---------------------------------------------------------------------

def score_journal(journal_text: str) -> dict:
    """
    Try Gemini first, then Fireworks, then fall back to the
    built-in keyword scorer.
    """

    result = score_with_gemini(journal_text)
    if result is not None:
        return result

    result = score_with_fireworks(journal_text)
    if result is not None:
        return result

    return keyword_score(journal_text)


# ---------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------

RESOURCE_LIBRARY = {
    "sleep_loss": [
        {
            "title": "Respite care overnight sitting services",
            "type": "respite_care",
        },
        {
            "title": "Sleep hygiene guide for caregivers",
            "type": "article",
        },
    ],
    "isolation": [
        {
            "title": "Local caregiver support group meetups",
            "type": "community",
        },
        {
            "title": "Online caregiver peer chat",
            "type": "community",
        },
    ],
    "resentment": [
        {
            "title": "Family caregiver counseling directory",
            "type": "counseling",
        },
        {
            "title": "Talking to family about sharing the load",
            "type": "article",
        },
    ],
    "physical_strain": [
        {
            "title": "Safe lifting and transfer techniques guide",
            "type": "article",
        },
        {
            "title": "Home health aide referral services",
            "type": "respite_care",
        },
    ],
    "emotional_exhaustion": [
        {
            "title": "Caregiver burnout helpline",
            "type": "helpline",
        },
        {
            "title": "Short-term respite stay programs",
            "type": "respite_care",
        },
    ],
}


# ---------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/journal")
def submit_journal(entry: JournalEntry):

    if not entry.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Journal entry cannot be empty.",
        )

    result = score_journal(entry.text)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "text": entry.text,
        "scores": result["scores"],
        "overall": result["overall"],
        "summary": result.get("summary", ""),
        "source": result["source"],
    }

    save_entry(record)

    return record


@app.get("/api/history")
def history():
    return load_entries()


@app.get("/api/resources")
def resources():

    entries = load_entries()

    if not entries:
        top_categories = CATEGORIES
    else:
        latest = entries[-1]["scores"]

        top_categories = sorted(
            latest,
            key=latest.get,
            reverse=True,
        )[:3]

    suggestions = []

    for category in top_categories:
        suggestions.extend(
            RESOURCE_LIBRARY.get(category, [])
        )

    return {
        "categories": top_categories,
        "resources": suggestions,
    }