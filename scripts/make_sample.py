"""Write a small stratified sample of tickets to commit to the repo.

The full dataset is reproducible and gitignored; this keeps a handful of rows per
team so readers can see the schema and text without regenerating anything.

Usage:
    python scripts/make_sample.py --data data/generated --per-team 10
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/generated")
    parser.add_argument("--per-team", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", default="data/samples/sample_tickets.csv")
    args = parser.parse_args()

    df = pd.read_csv(Path(args.data) / "tickets.csv")
    parts = [
        g.sample(n=min(args.per_team, len(g)), random_state=args.seed)
        for _, g in df.groupby("team")
    ]
    sample = pd.concat(parts).sort_values("created_at").reset_index(drop=True)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(out, index=False)
    print(f"Wrote {len(sample)} rows ({sample['team'].nunique()} teams) to {out}")


if __name__ == "__main__":
    main()
