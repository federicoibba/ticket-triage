# Data Card — Synthetic Ticket-Triage Dataset

Generated: 2026-10-08T23:21:13  
Rows: 5000  
Seed: 42  
Date range: 2023-01-01 02:16:04 -> 2025-12-30 19:42:01

## Provenance

Fully **synthetic**. Ticket text is assembled deterministically from a
frozen, LLM-authored phrase pool (`data/phrases/`). No real customer or
work data was used. Ground-truth `team` is known by construction.

## Label semantics

`team` is the target: the functional team that owns the ticket. `product`
is an input feature. Teams may span several products.

## Class distribution (`team`)

| team | count | share |
|---|---:|---:|
| Data Platform | 1515 | 30.3% |
| Mobile Apps | 810 | 16.2% |
| Search & Discovery | 523 | 10.5% |
| Reporting & Analytics | 449 | 9.0% |
| Infrastructure & DevOps | 328 | 6.6% |
| API & Integrations | 300 | 6.0% |
| Security & Compliance | 231 | 4.6% |
| Notifications & Messaging | 198 | 4.0% |
| Web Frontend | 196 | 3.9% |
| Auth & Identity | 178 | 3.6% |
| Payments & Billing | 172 | 3.4% |
| Onboarding & Accounts | 100 | 2.0% |

## Products

- Cohort: 1379 (27.6%)
- Delve: 1270 (25.4%)
- Atlas: 1261 (25.2%)
- Beacon: 648 (13.0%)
- Ember: 442 (8.8%)

## Ticket types

- bug: 2769 (55.4%)
- question: 704 (14.1%)
- feature_request: 619 (12.4%)
- incident: 505 (10.1%)
- dispute: 403 (8.1%)

## Leakage notes

These columns are only known **after resolution** and must NOT be used
as model inputs:

- `resolution`
- `resolution_hours`
- `reassignment_count`
- `team_path`

`intake_component` is a *human* hint present at intake; it is correct
only ~70% of the time and may mislead a model.

## Difficulty knobs (this run)

- `zipf_s`: 1.0
- `ambiguity_rate`: 0.1
- `intake_component_accuracy`: 0.7
- `label_noise_rate`: 0.05
- `typo_rate`: 0.03, `casing_rate`: 0.02
- `reassignment_prob`: 0.25
- `drift`: enabled=True, start=2025-01-01
- `unroutable_rate`: 0.0

## Known limitations

- Template/pool saturation: text diversity is bounded by the phrase pool.
- Artificial ambiguity and label noise are injected, not observed.
- Vocabulary drift is simulated by appending phrases, not by re-training.
- Intended for **method/pipeline benchmarking**, not production accuracy.
