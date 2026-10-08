# Data Card — Synthetic Ticket-Triage Dataset

Generated: 2026-10-08T23:21:16  
Rows: 20000  
Seed: 42  
Date range: 2023-01-01 01:27:44 -> 2025-12-30 23:10:47

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
| Data Platform | 6829 | 34.1% |
| Mobile Apps | 2947 | 14.7% |
| Search & Discovery | 1895 | 9.5% |
| Reporting & Analytics | 1768 | 8.8% |
| API & Integrations | 1278 | 6.4% |
| Infrastructure & DevOps | 1036 | 5.2% |
| Web Frontend | 790 | 4.0% |
| Security & Compliance | 718 | 3.6% |
| Auth & Identity | 639 | 3.2% |
| Unroutable | 630 | 3.1% |
| Notifications & Messaging | 595 | 3.0% |
| Payments & Billing | 453 | 2.3% |
| Onboarding & Accounts | 422 | 2.1% |

## Products

- Cohort: 6050 (30.2%)
- Delve: 5584 (27.9%)
- Atlas: 4621 (23.1%)
- Beacon: 2351 (11.8%)
- Ember: 1394 (7.0%)

## Ticket types

- bug: 10928 (54.6%)
- question: 3003 (15.0%)
- feature_request: 2431 (12.2%)
- incident: 2022 (10.1%)
- dispute: 1616 (8.1%)

## Leakage notes

These columns are only known **after resolution** and must NOT be used
as model inputs:

- `resolution`
- `resolution_hours`
- `reassignment_count`
- `team_path`

`intake_component` is a *human* hint present at intake; it is correct
only ~55% of the time and may mislead a model.

## Difficulty knobs (this run)

- `zipf_s`: 1.2
- `ambiguity_rate`: 0.25
- `intake_component_accuracy`: 0.55
- `label_noise_rate`: 0.12
- `typo_rate`: 0.06, `casing_rate`: 0.04
- `reassignment_prob`: 0.35
- `drift`: enabled=True, start=2025-01-01
- `unroutable_rate`: 0.03

## Known limitations

- Template/pool saturation: text diversity is bounded by the phrase pool.
- Artificial ambiguity and label noise are injected, not observed.
- Vocabulary drift is simulated by appending phrases, not by re-training.
- Intended for **method/pipeline benchmarking**, not production accuracy.
