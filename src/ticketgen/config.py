"""Config loading."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from . import taxonomy as tax


@dataclass
class Config:
    seed: int = 42
    n_tickets: int = 20000
    date_start: str = "2023-01-01"
    date_end: str = "2025-12-31"
    zipf_s: float = 1.0
    ambiguity_rate: float = 0.10
    intake_component_accuracy: float = 0.70
    label_noise_rate: float = 0.05
    typo_rate: float = 0.03
    casing_rate: float = 0.02
    reassignment_prob: float = 0.25
    error_signature_rate: float = 0.30
    drift_enabled: bool = True
    drift_start: str = "2025-01-01"
    drift_rate: float = 0.40
    unroutable_rate: float = 0.0
    products: list[str] = field(default_factory=lambda: list(tax.PRODUCTS))
    teams: list[str] = field(default_factory=lambda: list(tax.TEAMS))
    phrase_dir: str = "data/phrases"
    out_dir: str = "data/generated"


def load_config(path: str | Path) -> Config:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    date_range = raw.pop("date_range", {})
    drift = raw.pop("drift", {})
    cfg = Config(**raw)
    if "start" in date_range:
        cfg.date_start = date_range["start"]
    if "end" in date_range:
        cfg.date_end = date_range["end"]
    if "enabled" in drift:
        cfg.drift_enabled = drift["enabled"]
    if "start" in drift:
        cfg.drift_start = drift["start"]
    if "rate" in drift:
        cfg.drift_rate = drift["rate"]
    return cfg
