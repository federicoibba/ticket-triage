"""Noise transforms: typos, casing jitter, and vocabulary drift."""

from __future__ import annotations

import random

_KEYBOARD = "abcdefghijklmnopqrstuvwxyz"


def _typo_word(word: str, rng: random.Random) -> str:
    if len(word) < 4 or not word.isalpha():
        return word
    op = rng.choice(["swap", "drop", "double", "replace"])
    i = rng.randrange(1, len(word) - 1)
    if op == "swap" and i + 1 < len(word):
        return word[:i] + word[i + 1] + word[i] + word[i + 2:]
    if op == "drop":
        return word[:i] + word[i + 1:]
    if op == "double":
        return word[:i] + word[i] + word[i:]
    return word[:i] + rng.choice(_KEYBOARD) + word[i + 1:]


def apply_typos(text: str, rng: random.Random, rate: float) -> str:
    if rate <= 0:
        return text
    words = text.split(" ")
    out = []
    for w in words:
        # Preserve leading capitalisation / punctuation roughly by only editing
        # the alphabetic core.
        core = w.strip(".,:;!?()[]")
        if core and rng.random() < rate:
            w = w.replace(core, _typo_word(core, rng), 1)
        out.append(w)
    return " ".join(out)


def apply_casing(text: str, rng: random.Random, rate: float) -> str:
    if rate <= 0 or not text:
        return text
    if rng.random() < rate:
        return text.lower()
    if rng.random() < rate * 0.5:
        return text.upper()
    return text


def apply_text_noise(text: str, rng: random.Random, typo_rate: float, casing_rate: float) -> str:
    text = apply_typos(text, rng, typo_rate)
    text = apply_casing(text, rng, casing_rate)
    return text


def inject_drift(text: str, rng: random.Random, drift_terms: list[str], rate: float = 0.4) -> str:
    """Append a drift phrase to simulate vocabulary change over time."""
    if not drift_terms or rng.random() > rate:
        return text
    term = rng.choice(drift_terms)
    if term in text:
        return text
    return f"{text} {term}".strip()
