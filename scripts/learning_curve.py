"""Learning curve: how accuracy scales with training-set size.

Usage:
    python scripts/learning_curve.py --data data/generated --sizes 500,1000,2500,5000,10000,14000
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import OneHotEncoder

import baseline as base  # scripts/ is on sys.path[0]


def run_size(train, test, n: int, seed: int) -> dict:
    sub = train.sample(n=min(n, len(train)), random_state=seed)
    y_train, y_test = sub[base.TARGET], test[base.TARGET]

    word = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    char = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, sublinear_tf=True)
    ohe = OneHotEncoder(handle_unknown="ignore")

    X_train = sparse.hstack([
        word.fit_transform(base._text(sub)),
        char.fit_transform(base._text(sub)),
        ohe.fit_transform(sub[base.META_COLS]),
    ]).tocsr()
    X_test = sparse.hstack([
        word.transform(base._text(test)),
        char.transform(base._text(test)),
        ohe.transform(test[base.META_COLS]),
    ]).tocsr()

    clf = LogisticRegression(max_iter=2000, C=5.0).fit(X_train, y_train)
    pred = clf.predict(X_test)
    proba = clf.predict_proba(X_test)
    return {
        "n_train": len(sub),
        "accuracy": round(accuracy_score(y_test, pred), 4),
        "macro_f1": round(f1_score(y_test, pred, average="macro"), 4),
        "top3": round(base.top_k_accuracy(proba, y_test.to_numpy(), clf.classes_, 3), 4),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/generated")
    parser.add_argument("--sizes", default="500,1000,2500,5000,10000,14000")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    train, _val, test = base._load(Path(args.data))
    sizes = [int(s) for s in args.sizes.split(",")]

    results = [run_size(train, test, n, args.seed) for n in sizes]

    print(f"{'n_train':>8} {'accuracy':>10} {'macro_f1':>10} {'top3':>8}")
    for r in results:
        print(f"{r['n_train']:>8} {r['accuracy']:>10} {r['macro_f1']:>10} {r['top3']:>8}")

    out = Path(args.out) if args.out else Path(args.data) / "learning_curve.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
