# Data Card — Synthetic Ticket-Triage Dataset

Generated: 2026-10-08T23:21:14  
Rows: 10000  
Seed: 42  
Date range: 2023-01-01 02:16:04 -> 2025-12-30 20:55:22

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
| Data Platform | 3020 | 30.2% |
| Mobile Apps | 1586 | 15.9% |
| Search & Discovery | 1046 | 10.5% |
| Reporting & Analytics | 889 | 8.9% |
| Infrastructure & DevOps | 632 | 6.3% |
| API & Integrations | 620 | 6.2% |
| Security & Compliance | 465 | 4.7% |
| Web Frontend | 426 | 4.3% |
| Notifications & Messaging | 391 | 3.9% |
| Auth & Identity | 352 | 3.5% |
| Payments & Billing | 339 | 3.4% |
| Onboarding & Accounts | 234 | 2.3% |

## Products

- Cohort: 2797 (28.0%)
- Delve: 2538 (25.4%)
- Atlas: 2485 (24.9%)
- Beacon: 1265 (12.7%)
- Ember: 915 (9.2%)

## Ticket types

- bug: 5525 (55.2%)
- question: 1469 (14.7%)
- feature_request: 1196 (12.0%)
- incident: 993 (9.9%)
- dispute: 817 (8.2%)

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
