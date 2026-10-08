"""Static taxonomy for the fictional ticket-triage dataset.

Products are input features; teams are the prediction target. Teams can span
several products (like Eclipse's ``UI`` component spanning multiple products),
which keeps routing non-trivial.
"""

from __future__ import annotations

PRODUCTS: list[str] = ["Atlas", "Beacon", "Cohort", "Delve", "Ember"]

TEAMS: list[str] = [
    "Payments & Billing",
    "Auth & Identity",
    "Search & Discovery",
    "Notifications & Messaging",
    "Web Frontend",
    "Mobile Apps",
    "API & Integrations",
    "Data Platform",
    "Reporting & Analytics",
    "Infrastructure & DevOps",
    "Onboarding & Accounts",
    "Security & Compliance",
]

# Which products each team handles. Most teams map to one or two products; a
# few (frontend, API, infra, security) span the whole suite.
TEAM_PRODUCTS: dict[str, list[str]] = {
    "Payments & Billing": ["Ember", "Atlas"],
    "Auth & Identity": ["Atlas", "Beacon"],
    "Search & Discovery": ["Atlas", "Cohort"],
    "Notifications & Messaging": ["Atlas", "Beacon", "Delve"],
    "Web Frontend": ["Atlas", "Cohort", "Ember"],
    "Mobile Apps": ["Beacon", "Atlas"],
    "API & Integrations": ["Delve", "Atlas", "Ember"],
    "Data Platform": ["Delve", "Cohort"],
    "Reporting & Analytics": ["Cohort", "Delve"],
    "Infrastructure & DevOps": ["Atlas", "Delve", "Cohort", "Beacon", "Ember"],
    "Onboarding & Accounts": ["Atlas", "Ember"],
    "Security & Compliance": ["Atlas", "Ember", "Delve"],
}

# Coarse component labels shown as the (imperfect) human intake hint.
TEAM_COMPONENT: dict[str, str] = {
    "Payments & Billing": "Billing",
    "Auth & Identity": "Identity",
    "Search & Discovery": "Search",
    "Notifications & Messaging": "Messaging",
    "Web Frontend": "Frontend",
    "Mobile Apps": "Mobile",
    "API & Integrations": "API",
    "Data Platform": "Data",
    "Reporting & Analytics": "Analytics",
    "Infrastructure & DevOps": "Infra",
    "Onboarding & Accounts": "Accounts",
    "Security & Compliance": "Security",
}

# Pairs that are easy to confuse; used to inject realistic label noise.
CONFUSABLE: dict[str, list[str]] = {
    "Payments & Billing": ["Onboarding & Accounts", "API & Integrations"],
    "Auth & Identity": ["Security & Compliance", "Onboarding & Accounts"],
    "Search & Discovery": ["Reporting & Analytics", "Web Frontend"],
    "Notifications & Messaging": ["Web Frontend", "API & Integrations"],
    "Web Frontend": ["Mobile Apps", "Search & Discovery"],
    "Mobile Apps": ["Web Frontend", "Auth & Identity"],
    "API & Integrations": ["Data Platform", "Notifications & Messaging"],
    "Data Platform": ["Reporting & Analytics", "API & Integrations"],
    "Reporting & Analytics": ["Data Platform", "Search & Discovery"],
    "Infrastructure & DevOps": ["Data Platform", "Security & Compliance"],
    "Onboarding & Accounts": ["Auth & Identity", "Payments & Billing"],
    "Security & Compliance": ["Auth & Identity", "Infrastructure & DevOps"],
}

UNROUTABLE = "Unroutable"


def component_of(team: str) -> str:
    return TEAM_COMPONENT.get(team, team)
