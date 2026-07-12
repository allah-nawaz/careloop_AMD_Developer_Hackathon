"""
scorer.py
Simple, readable burnout scoring logic for CareLoop.

This file has two jobs:
1. keyword_score()  -> a rule-based fallback scorer that works with zero
                        external cost, so the app never fully breaks even
                        if no AI key is configured or the API call fails.
2. build_ai_prompt() -> the instruction we send to whichever AI model is
                        wired up in main.py (Gemini, Fireworks, etc).

Keeping this logic in its own file means main.py stays focused on
routing, and this file stays focused on "how do we turn a journal
entry into a burnout score."
"""

import re

# The five categories CareLoop tracks. Keep this list as the single
# source of truth - both the fallback scorer and the AI prompt use it.
CATEGORIES = [
    "sleep_loss",
    "isolation",
    "resentment",
    "physical_strain",
    "emotional_exhaustion",
]

# Simple keyword banks per category. This is intentionally basic -
# it is a safety net, not the "smart" part of the app. The AI model
# is what does the real reasoning when it's available.
KEYWORDS = {
    "sleep_loss": [
        "haven't slept", "havent slept", "can't sleep", "cant sleep",
        "no sleep", "exhausted", "tired all the time", "up all night",
        "insomnia", "3am", "3 am", "woke up again",
    ],
    "isolation": [
        "no one calls", "nobody checks", "alone", "isolated", "no friends",
        "haven't left the house", "havent left the house", "no time for myself",
        "cancelled plans", "canceled plans", "no one to talk to",
    ],
    "resentment": [
        "angry", "resent", "unfair", "why me", "sick of this",
        "no one helps", "nobody helps", "tired of doing everything",
        "frustrated", "bitter",
    ],
    "physical_strain": [
        "back hurts", "in pain", "exhausted physically", "can't lift",
        "cant lift", "sore", "injury", "hurts to move", "no energy",
    ],
    "emotional_exhaustion": [
        "burnt out", "burned out", "numb", "can't do this anymore",
        "cant do this anymore", "crying", "overwhelmed", "hopeless",
        "breaking down", "want to give up",
    ],
}


def _normalize(text: str) -> str:
    """Lowercase and strip punctuation so 'haven't' and 'havent' both match."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    return text


def keyword_score(journal_text: str) -> dict:
    """
    A rule-based fallback: counts keyword hits per category and turns
    that into a 0-10 score. This runs when no AI key is configured,
    or if the AI call fails, so the app degrades gracefully instead
    of breaking.
    """
    normalized = _normalize(journal_text)
    scores = {}

    for category, phrases in KEYWORDS.items():
        hits = sum(1 for phrase in phrases if phrase in normalized)
        # Cap at 10, roughly 2.5 points per matching phrase.
        scores[category] = min(10, hits * 3)

    overall = round(sum(scores.values()) / len(scores), 1)

    return {
        "scores": scores,
        "overall": overall,
        "source": "fallback_keyword_scorer",
    }


def build_ai_prompt(journal_text: str) -> str:
    """
    The instruction sent to the AI model. Asks for strict JSON so
    main.py can parse it directly with no extra text to strip.
    """
    categories_list = ", ".join(CATEGORIES)
    return f"""You are a careful, compassionate assistant that reads a caregiver's
voice journal entry and scores their burnout risk. Do not diagnose any
medical or mental health condition. Only reflect what is written.

Score each of these categories from 0 (no signs) to 10 (severe signs):
{categories_list}

Journal entry:
\"\"\"{journal_text}\"\"\"

Respond with ONLY valid JSON, no other text, in this exact shape:
{{
  "sleep_loss": 0,
  "isolation": 0,
  "resentment": 0,
  "physical_strain": 0,
  "emotional_exhaustion": 0,
  "summary": "one short, kind sentence reflecting what was written"
}}
"""


def overall_from_ai(ai_scores: dict) -> float:
    """Given the five category scores from the AI, compute an overall average."""
    values = [ai_scores.get(c, 0) for c in CATEGORIES]
    return round(sum(values) / len(values), 1)
