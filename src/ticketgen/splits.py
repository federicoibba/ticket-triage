"""Temporal train/val/test splits."""

from __future__ import annotations

from pathlib import Path

from .generate import write_csv
from .schema import Ticket

TRAIN_FRAC = 0.70
VAL_FRAC = 0.15
# test gets the remainder


def temporal_split(rows: list[Ticket], train_frac: float = TRAIN_FRAC,
                   val_frac: float = VAL_FRAC) -> dict[str, list[Ticket]]:
    ordered = sorted(rows, key=lambda r: r.created_at)
    n = len(ordered)
    n_train = int(n * train_frac)
    n_val = int(n * val_frac)
    return {
        "train": ordered[:n_train],
        "val": ordered[n_train:n_train + n_val],
        "test": ordered[n_train + n_val:],
    }


def write_splits(rows: list[Ticket], out_dir: str | Path) -> dict[str, Path]:
    out = Path(out_dir) / "splits"
    parts = temporal_split(rows)
    paths = {}
    for name, part in parts.items():
        paths[name] = write_csv(part, out / f"{name}.csv")
    return paths
