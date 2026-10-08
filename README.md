# Ticket Triage — Synthetic Dataset

A reproducible, fully synthetic dataset for a **multi-product ticket-triage** PoC:
given a ticket, predict which functional **team** should own it.

It is a _hybrid_ generator: realistic ticket text comes from a frozen, LLM-authored
phrase pool (`data/phrases/`), while ticket assembly is deterministic Python. That
means ground-truth labels are known by construction and difficulty is tunable —
ideal for a blog post that studies how accuracy responds to ambiguity and noise.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Validate the frozen phrase pool
python scripts/build_phrase_pool.py --check

# Generate 20k tickets + temporal splits + data card
python -m ticketgen.cli generate --config config/default.yaml --with-splits --with-datacard
# (run from repo root; PYTHONPATH=src is applied automatically below)
```

If `python -m ticketgen.cli` cannot find the package, set `PYTHONPATH=src`:

```bash
PYTHONPATH=src python -m ticketgen.cli generate --config config/default.yaml --with-splits --with-datacard
```

Baseline classifier (TF-IDF word + char n-grams, optional metadata, logistic regression):

```bash
python scripts/baseline.py --data data/generated
python scripts/baseline.py --data data/generated --no-metadata
python scripts/learning_curve.py --data data/generated
```

## Observed results (seed 42)

| setup                            | accuracy | macro-F1 | top-3 |
| -------------------------------- | -------: | -------: | ----: |
| majority class                   |    0.305 |        — |     — |
| default (20k), text only         |    0.896 |    0.884 | 0.970 |
| default (20k), text + metadata   |    0.908 |    0.893 | 0.984 |
| hard (20k, high ambiguity/noise) |    0.760 |    0.649 | 0.927 |

Learning curve (accuracy vs training size): 0.870 (500) → 0.897 (5k) → 0.906 (10k)
→ 0.909 (14k), i.e. diminishing returns after ~10k. Confusion concentrates on the
injected confusable pairs (API↔Data Platform, Reporting↔Data Platform,
Web Frontend↔Mobile, Auth↔Security).

## What it generates

- `data/generated/tickets.csv` — the dataset
- `data/generated/splits/{train,val,test}.csv` — fixed **temporal** splits (70/15/15)
- `data/generated/datacard.md` — provenance, class distribution, leakage notes

## What's committed

The generated datasets **are committed** so readers can browse and train without
regenerating anything:

- `data/phrases/` — the frozen phrase pool (the non-derivable input)
- `data/generated{,_small,_medium,_hard}/tickets.csv` — the datasets
- `data/generated*/datacard.md` — provenance, class distribution, leakage notes
- `data/generated/learning_curve.csv` — results
- `data/samples/sample_tickets.csv` — a small 120-row sample

Ignored: `data/*/splits/` only — the temporal 70/15/15 split is a deterministic
function of `tickets.csv`, and `scripts/baseline.py` recreates it automatically.

Regeneration **overwrites** these files in place:

```bash
PYTHONPATH=src python -m ticketgen.cli generate --config config/default.yaml --with-splits --with-datacard
```

Schema highlights: `ticket_id, created_at, product, team (target), title, description,
type, priority, severity, channel, reporter_type, customer_tier, intake_component,
reassignment_count, team_path, resolution, resolution_hours`.

## Design

- **5 fictional products** (Atlas, Beacon, Cohort, Delve, Ember) × **12 teams**.
  Teams can span multiple products, so routing is non-trivial.
- **Zipf class imbalance** (`zipf_s`) — a few teams get most tickets, like reality.
- **Leakage discipline** — `resolution*`, `team_path`, `reassignment_count` are
  resolution-time fields and must not be model inputs.
- **`intake_component`** is a human hint present at intake that is only correct
  ~70% of the time — a realistic shortcut a model can over-rely on.

## Difficulty knobs

Set in `config/*.yaml`:

| knob                        | effect                                                      |
| --------------------------- | ----------------------------------------------------------- |
| `zipf_s`                    | class imbalance (higher = more skewed)                      |
| `ambiguity_rate`            | share of generic, un-routable-sounding tickets              |
| `intake_component_accuracy` | how often the intake hint is correct                        |
| `label_noise_rate`          | share of mislabeled tickets                                 |
| `typo_rate`, `casing_rate`  | text noise                                                  |
| `reassignment_prob`         | tickets that bounced between teams                          |
| `drift`                     | vocabulary change after a cutoff date (temporal robustness) |
| `unroutable_rate`           | optional `Unroutable` fallback class (off by default)       |

Presets: `config/small.yaml` (5k), `config/medium.yaml` (10k), `config/default.yaml`
(20k), `config/hard.yaml` (high ambiguity + noise). All share the same seed, so you
can plot learning curves and difficulty sweeps.

## Regenerating the phrase pool with an LLM

The committed pool is already frozen. To refresh it:

```bash
OPENAI_API_KEY=... python scripts/build_phrase_pool.py --model gpt-4o-mini --out data/phrases/generated
```

## Intended use

Method/pipeline benchmarking, teaching, and blog experiments. **Not** a proxy for
production accuracy — see the data card's limitations.
