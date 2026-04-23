# -*- coding: utf-8 -*-
"""
Grouped bar chart: one cluster per experiment, three bars (accuracy, clarity, groundedness).

Reads either:
  - manual scoring CSV (per-question rows with accuracy, clarity, groundedness), or
  - results_summary.csv (mean_* columns).

Usage:
    python plot_experiment_scores.py
    python plot_experiment_scores.py --scores results/manual_scores_completed.csv --out results/experiment_scores_bars.png
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

METRICS = ("accuracy", "clarity", "groundedness")


def _natural_exp_order(names: list[str]) -> list[str]:
    def key(s: str) -> tuple:
        s = s.strip()
        if s.startswith("exp") and s[3:].isdigit():
            return (0, int(s[3:]))
        return (1, s)

    return sorted(names, key=key)


def load_from_manual(path: Path) -> tuple[list[str], list[float], list[float], list[float]]:
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    sums: dict[str, list[float]] = defaultdict(lambda: [0.0, 0.0, 0.0])
    counts: dict[str, int] = defaultdict(int)
    for r in rows:
        e = (r.get("experiment_name") or "").strip()
        if not e:
            continue
        for i, m in enumerate(METRICS):
            v = (r.get(m) or "").strip().replace(",", ".")
            if v:
                sums[e][i] += float(v)
        counts[e] += 1
    names = _natural_exp_order(list(sums.keys()))
    acc = [sums[n][0] / counts[n] for n in names]
    clar = [sums[n][1] / counts[n] for n in names]
    grnd = [sums[n][2] / counts[n] for n in names]
    return names, acc, clar, grnd


def load_from_summary(path: Path) -> tuple[list[str], list[float], list[float], list[float]]:
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    by_name: dict[str, tuple[float, float, float]] = {}
    for r in rows:
        e = (r.get("experiment_name") or "").strip()
        if not e:
            continue
        by_name[e] = (
            float(r["mean_accuracy"]),
            float(r["mean_clarity"]),
            float(r["mean_groundedness"]),
        )
    names = _natural_exp_order(list(by_name.keys()))
    acc = [by_name[n][0] for n in names]
    clar = [by_name[n][1] for n in names]
    grnd = [by_name[n][2] for n in names]
    return names, acc, clar, grnd


def load_data(path: Path) -> tuple[list[str], list[float], list[float], list[float]]:
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    if not rows:
        raise ValueError("Empty CSV")
    if "mean_accuracy" in fieldnames:
        return load_from_summary(path)
    return load_from_manual(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Plot mean scores by experiment (grouped bars)")
    root = Path(__file__).resolve().parent
    parser.add_argument(
        "--scores",
        type=Path,
        default=root / "results" / "manual_scores_completed.csv",
        help="Manual scores CSV or results_summary.csv",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=root / "results" / "experiment_scores_bars.png",
        help="Output PNG path",
    )
    parser.add_argument(
        "--title",
        type=str,
        default="Mean scores by experiment",
    )
    args = parser.parse_args()

    names, acc, clar, grnd = load_data(args.scores)
    if not names:
        raise SystemExit("No experiments found in CSV")

    x = np.arange(len(names), dtype=float)
    width = 0.25
    fig, ax = plt.subplots(figsize=(max(8.0, len(names) * 1.2), 5.0))
    ax.bar(x - width, acc, width, label="Accuracy", color="#4477AA", edgecolor="white", linewidth=0.5)
    ax.bar(x, clar, width, label="Clarity", color="#EE8866", edgecolor="white", linewidth=0.5)
    ax.bar(x + width, grnd, width, label="Groundedness", color="#66C0A5", edgecolor="white", linewidth=0.5)

    ax.set_xlabel("Experiment")
    ax.set_ylabel("Score (mean)")
    ax.set_title(args.title)
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=0)
    ax.legend(frameon=True, loc="upper right")
    ax.set_ylim(bottom=0)
    ymax = max(max(acc) if acc else 0, max(clar) if clar else 0, max(grnd) if grnd else 0)
    ax.set_ylim(0, min(ymax * 1.15, ymax + 0.5) if ymax > 0 else 1.0)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    fig.tight_layout()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=150)
    plt.close(fig)
    print(f"Saved {args.out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
