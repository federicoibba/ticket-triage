"""Emit a data card documenting the synthetic dataset."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path

from .config import Config
from .schema import RESOLUTION_TIME_COLUMNS, Ticket


def _pct(n: int, total: int) -> str:
    return f"{100 * n / total:.1f}%"


def build_datacard(rows: list[Ticket], cfg: Config) -> str:
    total = len(rows)
    teams = Counter(r.team for r in rows)
    products = Counter(r.product for r in rows)
    types = Counter(r.type for r in rows)
    dates = sorted(r.created_at for r in rows)

    lines: list[str] = []
    lines.append("# Data Card — Synthetic Ticket-Triage Dataset\n")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}  ")
    lines.append(f"Rows: {total}  ")
    lines.append(f"Seed: {cfg.seed}  ")
    lines.append(f"Date range: {dates[0]} -> {dates[-1]}\n")

    lines.append("## Provenance\n")
    lines.append("Fully **synthetic**. Ticket text is assembled deterministically from a")
    lines.append("frozen, LLM-authored phrase pool (`data/phrases/`). No real customer or")
    lines.append("work data was used. Ground-truth `team` is known by construction.\n")

    lines.append("## Label semantics\n")
    lines.append("`team` is the target: the functional team that owns the ticket. `product`")
    lines.append("is an input feature. Teams may span several products.\n")

    lines.append("## Class distribution (`team`)\n")
    lines.append("| team | count | share |")
    lines.append("|---|---:|---:|")
    for team, n in teams.most_common():
        lines.append(f"| {team} | {n} | {_pct(n, total)} |")
    lines.append("")

    lines.append("## Products\n")
    for p, n in products.most_common():
        lines.append(f"- {p}: {n} ({_pct(n, total)})")
    lines.append("")

    lines.append("## Ticket types\n")
    for t, n in types.most_common():
        lines.append(f"- {t}: {n} ({_pct(n, total)})")
    lines.append("")

    lines.append("## Leakage notes\n")
    lines.append("These columns are only known **after resolution** and must NOT be used")
    lines.append("as model inputs:\n")
    for c in RESOLUTION_TIME_COLUMNS:
        lines.append(f"- `{c}`")
    lines.append("")
    lines.append("`intake_component` is a *human* hint present at intake; it is correct")
    lines.append(f"only ~{int(cfg.intake_component_accuracy * 100)}% of the time and may mislead a model.\n")

    lines.append("## Difficulty knobs (this run)\n")
    lines.append(f"- `zipf_s`: {cfg.zipf_s}")
    lines.append(f"- `ambiguity_rate`: {cfg.ambiguity_rate}")
    lines.append(f"- `intake_component_accuracy`: {cfg.intake_component_accuracy}")
    lines.append(f"- `label_noise_rate`: {cfg.label_noise_rate}")
    lines.append(f"- `typo_rate`: {cfg.typo_rate}, `casing_rate`: {cfg.casing_rate}")
    lines.append(f"- `reassignment_prob`: {cfg.reassignment_prob}")
    lines.append(f"- `drift`: enabled={cfg.drift_enabled}, start={cfg.drift_start}")
    lines.append(f"- `unroutable_rate`: {cfg.unroutable_rate}\n")

    lines.append("## Known limitations\n")
    lines.append("- Template/pool saturation: text diversity is bounded by the phrase pool.")
    lines.append("- Artificial ambiguity and label noise are injected, not observed.")
    lines.append("- Vocabulary drift is simulated by appending phrases, not by re-training.")
    lines.append("- Intended for **method/pipeline benchmarking**, not production accuracy.\n")

    return "\n".join(lines)


def write_datacard(rows: list[Ticket], cfg: Config, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_datacard(rows, cfg), encoding="utf-8")
    return path
