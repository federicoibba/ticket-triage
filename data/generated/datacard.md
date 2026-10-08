# Data Card — Synthetic Ticket-Triage Dataset

Generated: 2026-10-08T23:21:12  
Rows: 20000  
Seed: 42  
Date range: 2023-01-01 02:16:04 -> 2025-12-30 23:14:01

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
| Data Platform | 6163 | 30.8% |
| Mobile Apps | 3096 | 15.5% |
| Search & Discovery | 2098 | 10.5% |
| Reporting & Analytics | 1793 | 9.0% |
| Infrastructure & DevOps | 1267 | 6.3% |
| API & Integrations | 1206 | 6.0% |
| Security & Compliance | 970 | 4.8% |
| Web Frontend | 814 | 4.1% |
| Notifications & Messaging | 785 | 3.9% |
| Auth & Identity | 679 | 3.4% |
| Payments & Billing | 636 | 3.2% |
| Onboarding & Accounts | 493 | 2.5% |

## Products

- Cohort: 5660 (28.3%)
- Delve: 5180 (25.9%)
- Atlas: 4965 (24.8%)
- Beacon: 2437 (12.2%)
- Ember: 1758 (8.8%)

## Ticket types

- bug: 10947 (54.7%)
- question: 2972 (14.9%)
- feature_request: 2469 (12.3%)
- incident: 1994 (10.0%)
- dispute: 1618 (8.1%)

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
