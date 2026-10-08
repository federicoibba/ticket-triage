"""Baseline ticket-triage classifier: TF-IDF (word + char) + linear model.

Usage:
    python scripts/baseline.py --data data/generated
    python scripts/baseline.py --data data/generated --no-metadata
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.preprocessing import OneHotEncoder

TEXT_COLS = ["title", "description"]
META_COLS = [
    "product",
    "type",
    "priority",
    "severity",
    "channel",
    "reporter_type",
    "customer_tier",
    "intake_component",
]
TARGET = "team"


def _load(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    splits = data_dir / "splits"
    if splits.exists():
        return tuple(pd.read_csv(splits / f"{n}.csv") for n in ("train", "val", "test"))
    df = pd.read_csv(data_dir / "tickets.csv")
    df = df.sort_values("created_at")
    n = len(df)
    return df.iloc[: int(0.7 * n)], df.iloc[int(0.7 * n): int(0.85 * n)], df.iloc[int(0.85 * n):]


def _text(df: pd.DataFrame) -> pd.Series:
    return (df["title"].fillna("") + " " + df["description"].fillna("")).str.lower()


def top_k_accuracy(proba: np.ndarray, y: np.ndarray, classes: np.ndarray, k: int) -> float:
    idx = np.argsort(-proba, axis=1)[:, :k]
    hits = [y[i] in classes[idx[i]] for i in range(len(y))]
    return float(np.mean(hits))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/generated")
    parser.add_argument("--no-metadata", action="store_true")
    args = parser.parse_args()

    data_dir = Path(args.data)
    train, val, test = _load(data_dir)
    print(f"train={len(train)} val={len(val)} test={len(test)}")

    y_train, y_test = train[TARGET], test[TARGET]

    word = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    char = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, sublinear_tf=True)
    xw = word.fit_transform(_text(train))
    xc = char.fit_transform(_text(train))
    blocks = [xw, xc]

    if not args.no_metadata:
        ohe = OneHotEncoder(handle_unknown="ignore")
        xm = ohe.fit_transform(train[META_COLS])
        blocks.append(xm)

    X_train = sparse.hstack(blocks).tocsr()
    test_blocks = [word.transform(_text(test)), char.transform(_text(test))]
    if not args.no_metadata:
        test_blocks.append(ohe.transform(test[META_COLS]))
    X_test = sparse.hstack(test_blocks).tocsr()

    # Majority baseline.
    majority = y_train.value_counts().idxmax()
    maj_acc = accuracy_score(y_test, [majority] * len(y_test))
    print(f"\nMajority class: {majority!r}  accuracy={maj_acc:.3f}")

    clf = LogisticRegression(max_iter=2000, C=5.0)
    clf.fit(X_train, y_train)

    pred = clf.predict(X_test)
    acc = accuracy_score(y_test, pred)
    macro = f1_score(y_test, pred, average="macro")
    print(f"LogReg accuracy={acc:.3f}  macro-F1={macro:.3f}")

    proba = clf.predict_proba(X_test)
    print(f"Top-3 accuracy={top_k_accuracy(proba, y_test.to_numpy(), clf.classes_, 3):.3f}")

    print("\nPer-class report (test):")
    print(classification_report(y_test, pred, zero_division=0))

    labels = clf.classes_
    print("Confusion matrix (rows=true, cols=pred):")
    cm = confusion_matrix(y_test, pred, labels=labels)
    header = "".join(f"{c[:6]:>8}" for c in labels)
    print(f"{'':>18}{header}")
    for i, c in enumerate(labels):
        print(f"{c[:16]:>18}" + "".join(f"{v:>8}" for v in cm[i]))


if __name__ == "__main__":
    main()
