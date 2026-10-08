"""One-time phrase-pool builder (the "hybrid" LLM step).

The repository ships a frozen, hand-authored pool in ``data/phrases/``. This
script documents how such a pool would be produced or refreshed with an LLM, and
can validate an existing pool without any network access.

Usage:
    # Validate the committed pool (no network):
    python scripts/build_phrase_pool.py --check

    # Print the prompt for a team (to copy into any LLM):
    python scripts/build_phrase_pool.py --prompt "Mobile Apps"

    # Generate with an OpenAI-compatible endpoint:
    OPENAI_API_KEY=... python scripts/build_phrase_pool.py \
        --model gpt-4o-mini --out data/phrases/generated

The output must satisfy ``ticketgen.phrases.validate_pools`` before use.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ticketgen import taxonomy as tax  # noqa: E402
from ticketgen.phrases import SLOTS, load_pools, validate_pools  # noqa: E402

PROMPT_TEMPLATE = """You are generating synthetic training data for a ticket-triage classifier.
Produce a JSON object for the team "{team}" that owns tickets in a fictional SaaS suite.
Return ONLY JSON with these keys, each an array of unique English strings:
{slots}

Rules:
- 8-12 entries per array.
- Do NOT include the literal team name "{team}" in any string.
- Descriptions should read like real support tickets (symptoms, impact, expectation).
- Keep it generic enough that a few tickets could plausibly belong to a neighbouring team.
"""


def build_prompt(team: str) -> str:
    return PROMPT_TEMPLATE.format(team=team, slots=", ".join(SLOTS))


def call_llm(prompt: str, model: str) -> dict:
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("Set OPENAI_API_KEY (or use --prompt to copy manually).")
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "temperature": 0.7,
    }).encode()
    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:  # noqa: S310
        payload = json.loads(resp.read())
    return json.loads(payload["choices"][0]["message"]["content"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate the committed pool")
    parser.add_argument("--prompt", metavar="TEAM", help="print the prompt for one team")
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--out", help="directory to write teams.json when generating")
    args = parser.parse_args()

    if args.check:
        teams, shared = load_pools()
        print(f"OK: {len(teams)} teams, slots={len(SLOTS)} each")
        return

    if args.prompt:
        print(build_prompt(args.prompt))
        return

    if not args.out:
        parser.error("provide --out <dir> to generate, or --check / --prompt")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    generated: dict = {}
    for team in tax.TEAMS:
        print(f"Generating {team} ...", file=sys.stderr)
        generated[team] = call_llm(build_prompt(team), args.model)

    # Merge with the shipped shared.json so validation passes.
    _, shared = load_pools()
    validate_pools(generated, shared)
    (out / "teams.json").write_text(json.dumps(generated, indent=2), encoding="utf-8")
    print(f"Wrote {out / 'teams.json'}")


if __name__ == "__main__":
    main()
