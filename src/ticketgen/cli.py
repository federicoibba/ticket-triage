"""Command-line entrypoint."""

from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_config
from .datacard import write_datacard
from .generate import generate, write_csv
from .splits import write_splits


def _cmd_generate(args: argparse.Namespace) -> None:
    cfg = load_config(args.config)
    rows = generate(cfg)
    out = Path(cfg.out_dir)
    path = write_csv(rows, out / "tickets.csv")
    print(f"Wrote {len(rows)} tickets to {path}")
    if args.with_splits:
        paths = write_splits(rows, out)
        for name, p in paths.items():
            print(f"  {name}: {p}")
    if args.with_datacard:
        card = write_datacard(rows, cfg, out / "datacard.md")
        print(f"  datacard: {card}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="ticketgen", description="Synthetic ticket-triage dataset")
    sub = parser.add_subparsers(dest="command", required=True)

    g = sub.add_parser("generate", help="generate the dataset")
    g.add_argument("--config", default="config/default.yaml")
    g.add_argument("--with-splits", action="store_true")
    g.add_argument("--with-datacard", action="store_true")
    g.set_defaults(func=_cmd_generate)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
