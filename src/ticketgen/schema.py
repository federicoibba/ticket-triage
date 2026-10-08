"""Ticket record schema and CSV serialization."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields

COLUMNS: list[str] = [
    "ticket_id",
    "created_at",
    "product",
    "team",
    "title",
    "description",
    "type",
    "priority",
    "severity",
    "channel",
    "reporter_type",
    "customer_tier",
    "intake_component",
    "reassignment_count",
    "team_path",
    "resolution",
    "resolution_hours",
]

# Columns that are only known *after* the ticket is resolved. They must never be
# used as model inputs for triage. Documented in the data card.
RESOLUTION_TIME_COLUMNS: list[str] = [
    "resolution",
    "resolution_hours",
    "reassignment_count",
    "team_path",
]


@dataclass
class Ticket:
    ticket_id: str
    created_at: str
    product: str
    team: str
    title: str
    description: str
    type: str
    priority: str
    severity: str
    channel: str
    reporter_type: str
    customer_tier: str
    intake_component: str
    reassignment_count: int = 0
    team_path: str = ""
    resolution: str = "resolved"
    resolution_hours: float = 0.0

    def to_row(self) -> dict:
        return asdict(self)


def rows_to_dicts(rows: list[Ticket]) -> list[dict]:
    return [r.to_row() for r in rows]
