"""Deterministic assembly of the synthetic ticket dataset."""

from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

from . import taxonomy as tax
from .config import Config
from .noise import apply_text_noise, inject_drift
from .phrases import load_pools
from .schema import COLUMNS, Ticket

TYPES = ["bug", "question", "feature_request", "incident", "dispute"]
TYPE_W = [0.55, 0.15, 0.12, 0.10, 0.08]

SEVERITIES = ["S1", "S2", "S3", "S4"]
SEVERITY_W = [0.08, 0.30, 0.50, 0.12]

PRIORITY_BY_SEVERITY = {
    "S1": [("P1", 0.7), ("P2", 0.3)],
    "S2": [("P2", 0.6), ("P3", 0.4)],
    "S3": [("P3", 0.7), ("P4", 0.3)],
    "S4": [("P4", 0.8), ("P3", 0.2)],
}

CHANNELS = ["email", "web", "chat", "api"]
CHANNEL_W = [0.35, 0.35, 0.20, 0.10]

REPORTERS = ["customer", "internal", "automated"]
REPORTER_W = [0.70, 0.25, 0.05]

TIERS = ["free", "pro", "enterprise"]
TIER_W = [0.50, 0.35, 0.15]

RESOLUTIONS = ["resolved", "duplicate", "wontfix", "worksforme"]
RESOLUTION_W = [0.90, 0.04, 0.03, 0.03]

BASE_HOURS = {"P1": 8.0, "P2": 24.0, "P3": 72.0, "P4": 168.0}


def _cap(s: str) -> str:
    return s[:1].upper() + s[1:] if s else s


def _weighted(rng: random.Random, options: list, weights: list) -> object:
    return rng.choices(options, weights=weights, k=1)[0]


def _zipf_weights(teams: list[str], s: float, rng: random.Random) -> list[float]:
    ranked = teams[:]
    rng.shuffle(ranked)
    weights = {t: 1.0 / ((i + 1) ** s) for i, t in enumerate(ranked)}
    return [weights[t] for t in teams]


def _fill(template: str, ctx: dict) -> str:
    return template.format(**ctx)


def _compose_text(rng: random.Random, team: str, product: str, pool: dict, shared: dict,
                  cfg: Config) -> tuple[str, str]:
    ctx = {
        "entity": rng.choice(pool["entities"]),
        "symptom": rng.choice(pool["symptoms"]),
        "action": rng.choice(pool["actions"]),
        "product": product,
    }
    title = _cap(_fill(rng.choice(pool["title_templates"]), ctx))

    opener = _fill(rng.choice(pool["description_openers"]), ctx)
    context = _fill(rng.choice(pool["description_context"]), ctx)
    impact = _cap(_fill(rng.choice(pool["description_impact"]), ctx))
    expected = _cap(_fill(rng.choice(pool["description_expected"]), ctx))
    description = f"{opener} {context}. {impact}. {expected}."

    if rng.random() < cfg.error_signature_rate:
        description += f" Error: {rng.choice(pool['error_signatures'])}."

    return title, description


def _generic_text(rng: random.Random, product: str, shared: dict) -> tuple[str, str]:
    title = rng.choice(shared["generic_titles"])
    description = _fill(rng.choice(shared["generic_descriptions"]), {"product": product})
    return title, description


def _make_ticket(rng: random.Random, idx: int, teams: list[str], team_w: list[float],
                 pools: dict, shared: dict, cfg: Config) -> Ticket:
    true_team = _weighted(rng, teams, team_w)
    product = rng.choice(tax.TEAM_PRODUCTS.get(true_team, cfg.products))

    title, description = _compose_text(rng, true_team, product, pools[true_team], shared, cfg)

    # Deliberate ambiguity: replace with generic, un-routable-sounding text.
    unroutable = cfg.unroutable_rate > 0 and rng.random() < cfg.unroutable_rate
    if unroutable:
        title, description = _generic_text(rng, product, shared)
        team = tax.UNROUTABLE
    elif rng.random() < cfg.ambiguity_rate:
        title, description = _generic_text(rng, product, shared)
        team = true_team
    else:
        team = true_team

    # Metadata.
    severity = _weighted(rng, SEVERITIES, SEVERITY_W)
    priority = _weighted(rng, *zip(*PRIORITY_BY_SEVERITY[severity]))
    ttype = _weighted(rng, TYPES, TYPE_W)
    channel = _weighted(rng, CHANNELS, CHANNEL_W)
    reporter = _weighted(rng, REPORTERS, REPORTER_W)
    tier = _weighted(rng, TIERS, TIER_W)

    # Intake component hint: sometimes right, sometimes misleading.
    if rng.random() < cfg.intake_component_accuracy:
        intake_component = tax.component_of(team if team != tax.UNROUTABLE else true_team)
    else:
        other = rng.choice([t for t in tax.TEAMS if t != true_team])
        intake_component = tax.component_of(other)

    # Reassignment history (resolution-time field, not a model input).
    if team != tax.UNROUTABLE and rng.random() < cfg.reassignment_prob:
        count = rng.randint(1, 3)
        start = rng.choice(tax.CONFUSABLE.get(true_team, tax.TEAMS))
        path = ">".join([start, true_team]) if start != true_team else true_team
        if count > 1:
            path = ">".join([start, "Triage", true_team])
    else:
        count = 0
        path = team

    resolution = _weighted(rng, RESOLUTIONS, RESOLUTION_W)
    hours = round(BASE_HOURS[priority] * rng.uniform(0.3, 3.0), 1)

    # Timestamp (uniform across the window).
    start = datetime.fromisoformat(cfg.date_start)
    end = datetime.fromisoformat(cfg.date_end)
    created = start + timedelta(seconds=rng.uniform(0, (end - start).total_seconds()))

    # Vocabulary drift after the cutoff.
    if cfg.drift_enabled and created >= datetime.fromisoformat(cfg.drift_start):
        description = inject_drift(description, rng, shared.get("drift_terms", []), cfg.drift_rate)

    # Text noise last so it affects everything.
    title = apply_text_noise(title, rng, cfg.typo_rate, cfg.casing_rate)
    description = apply_text_noise(description, rng, cfg.typo_rate, cfg.casing_rate)

    # Label noise: flip to a confusable neighbour (text stays as generated).
    if team != tax.UNROUTABLE and rng.random() < cfg.label_noise_rate:
        team = rng.choice(tax.CONFUSABLE.get(team, tax.TEAMS))

    return Ticket(
        ticket_id=f"TKT-{idx:06d}",
        created_at=created.strftime("%Y-%m-%d %H:%M:%S"),
        product=product,
        team=team,
        title=title,
        description=description,
        type=ttype,
        priority=priority,
        severity=severity,
        channel=channel,
        reporter_type=reporter,
        customer_tier=tier,
        intake_component=intake_component,
        reassignment_count=count,
        team_path=path,
        resolution=resolution,
        resolution_hours=hours,
    )


def generate(cfg: Config) -> list[Ticket]:
    pools, shared = load_pools(cfg.phrase_dir)
    rng = random.Random(cfg.seed)
    teams = cfg.teams
    team_w = _zipf_weights(teams, cfg.zipf_s, rng)
    return [
        _make_ticket(rng, i + 1, teams, team_w, pools, shared, cfg)
        for i in range(cfg.n_tickets)
    ]


def write_csv(rows: list[Ticket], path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.to_row())
    return path
