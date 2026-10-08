"""Convert the synthetic ticket dataset into the Unsloth decision-model format.

Unsloth's ``FastDecisionModel`` expects rows with three columns, each a JSON
string (see https://unsloth.ai/docs/basics/train-your-own-decision-model-with-unsloth):

    state      - the input (here: ticket text + intake metadata)
    questions  - the decisions to make (here: a single 12-option ``choice``)
    gold       - the gold answer(s) (here: the owning team)

We emit parquet (not JSONL) because the identical ``questions`` blob repeats on
every row and compresses to almost nothing.

Usage:
    python scripts/to_decision_dataset.py --data data/generated --out data/decisions
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ticketgen import taxonomy as tax  # noqa: E402

TARGET = "team"

# Intake-time metadata (same set the TF-IDF baseline used). Resolution-time
# fields (resolution, resolution_hours, reassignment_count, team_path) are
# deliberately excluded to avoid leakage.
META_COLS = [
    "product",
    "type",
    "priority",
    "severity",
    "channel",
    "reporter_type",
    "customer_tier",
    "intake_component",
]

# Short, terse option descriptions. The docs warn that options share a token
# budget and labels get trimmed past ~20 described options, so keep these short.
TEAM_CRITERIA: dict[str, str] = {
    "Payments & Billing": "Payments, invoices, refunds, subscriptions, checkout.",
    "Auth & Identity": "Login, SSO, MFA, password reset, sessions, API keys.",
    "Search & Discovery": "Search, ranking, filters, autocomplete, indexing.",
    "Notifications & Messaging": "Email, push, in-app messages, digests, webhooks.",
    "Web Frontend": "Web UI, layout, rendering, forms, accessibility.",
    "Mobile Apps": "iOS and Android apps, offline sync, app crashes.",
    "API & Integrations": "Public API, SDKs, webhooks, rate limits, pagination.",
    "Data Platform": "Ingestion, ETL, schemas, streaming, warehouses.",
    "Reporting & Analytics": "Dashboards, reports, metrics, exports, aggregation.",
    "Infrastructure & DevOps": "Deploys, scaling, clusters, DNS, CDN, alerts.",
    "Onboarding & Accounts": "Signup, invites, workspaces, roles, trial setup.",
    "Security & Compliance": "Audit logs, access control, PII, policies, keys.",
}


def slug(team: str) -> str:
    """'Payments & Billing' -> 'payments_billing' (valid option key)."""
    return re.sub(r"[^a-z0-9]+", "_", team.lower().replace("&", " ")).strip("_")


SLUGS: dict[str, str] = {team: slug(team) for team in tax.TEAMS}
SLUG_TO_TEAM: dict[str, str] = {v: k for k, v in SLUGS.items()}


def build_questions() -> str:
    criteria = {SLUGS[t]: TEAM_CRITERIA[t] for t in tax.TEAMS}
    questions = {
        "team": {
            "type": "choice",
            "instructions": "Which functional team should own this ticket?",
            "criteria": criteria,
        }
    }
    return json.dumps(questions)


def build_state(row: pd.Series) -> str:
    state = {col: row[col] for col in META_COLS}
    state["title"] = row["title"]
    state["description"] = row["description"]
    return json.dumps(state, ensure_ascii=False)


def build_gold(team: str) -> str:
    label = SLUGS[team]
    probabilities = {SLUGS[t]: (1.0 if t == team else 0.0) for t in tax.TEAMS}
    gold = {
        "team": {
            "type": "choice",
            "label": label,
            "confidence": 1.0,
            "probabilities": probabilities,
        }
    }
    return json.dumps(gold)


def to_decision_frame(df: pd.DataFrame, questions: str) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticket_id": df["ticket_id"].to_numpy(),
            "state": df.apply(build_state, axis=1).to_numpy(),
            "questions": questions,
            "gold": df[TARGET].map(build_gold).to_numpy(),
        }
    )


def _load_splits(data_dir: Path) -> dict[str, pd.DataFrame]:
    splits = data_dir / "splits"
    if splits.exists():
        return {n: pd.read_csv(splits / f"{n}.csv") for n in ("train", "val", "test")}
    df = pd.read_csv(data_dir / "tickets.csv").sort_values("created_at").reset_index(drop=True)
    n = len(df)
    return {
        "train": df.iloc[: int(0.70 * n)].copy(),
        "val": df.iloc[int(0.70 * n): int(0.85 * n)].copy(),
        "test": df.iloc[int(0.85 * n):].copy(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/generated")
    parser.add_argument("--out", default="data/decisions")
    parser.add_argument("--train-subset", type=int, default=5000,
                        help="rows for the quick-run train file (0 = full)")
    parser.add_argument("--sample", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    data_dir = Path(args.data)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    splits = _load_splits(data_dir)
    questions = build_questions()

    written: list[Path] = []

    def write(name: str, df: pd.DataFrame) -> None:
        frame = to_decision_frame(df, questions)
        path = out / name
        frame.to_parquet(path, index=False)
        written.append(path)
        print(f"  {name:<24} {len(frame):>6} rows  ({path.stat().st_size / 1024:.0f} KB)")

    print(f"Writing decision dataset to {out}/  (slug keys: {len(SLUGS)} teams)")

    # Full train, plus a deterministic subset for the first Colab run.
    write("train.parquet", splits["train"])
    n = args.train_subset
    if n and n < len(splits["train"]):
        subset = splits["train"].sample(n=n, random_state=args.seed)
        write(f"train_{n // 1000}k.parquet", subset)
    write("val.parquet", splits["val"])
    write("test.parquet", splits["test"])

    sample = splits["train"].sample(n=min(args.sample, len(splits["train"])), random_state=args.seed)
    write("sample.parquet", sample)

    # Sanity report.
    subset = splits["train"].sample(n=min(n, len(splits["train"])), random_state=args.seed) if n else splits["train"]
    print("\nTeam distribution in the quick-run subset:")
    print(subset[TARGET].value_counts().to_string())

    print("\nWrote:")
    for p in written:
        print(f"  {p}")


if __name__ == "__main__":
    main()
