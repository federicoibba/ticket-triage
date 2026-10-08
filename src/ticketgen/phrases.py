"""Load and validate the frozen phrase pools."""

from __future__ import annotations

import json
from pathlib import Path

from . import taxonomy as tax

SLOTS = [
    "entities",
    "symptoms",
    "actions",
    "title_templates",
    "description_openers",
    "description_context",
    "description_impact",
    "description_expected",
    "error_signatures",
]


def _default_phrase_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "phrases"


def load_pools(phrase_dir: str | Path | None = None) -> tuple[dict, dict]:
    """Return ``(teams, shared)`` phrase dictionaries."""
    base = Path(phrase_dir) if phrase_dir else _default_phrase_dir()
    teams = json.loads((base / "teams.json").read_text(encoding="utf-8"))
    shared = json.loads((base / "shared.json").read_text(encoding="utf-8"))
    validate_pools(teams, shared)
    return teams, shared


def validate_pools(teams: dict, shared: dict) -> None:
    missing = [t for t in tax.TEAMS if t not in teams]
    if missing:
        raise ValueError(f"phrase pool missing teams: {missing}")

    for team, slots in teams.items():
        for slot in SLOTS:
            values = slots.get(slot)
            if not values:
                raise ValueError(f"team {team!r} has empty/missing slot {slot!r}")
            if len(set(values)) != len(values):
                raise ValueError(f"team {team!r} slot {slot!r} has duplicates")

    for slot in ("generic_titles", "generic_descriptions", "drift_terms"):
        if not shared.get(slot):
            raise ValueError(f"shared pool missing slot {slot!r}")
