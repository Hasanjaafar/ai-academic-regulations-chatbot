# -*- coding: utf-8 -*-
"""
Build an empty manual scoring sheet from experiment_outputs.csv (one row per run).

Fill in accuracy, clarity, groundedness (e.g. 1–5 or your rubric), then use
build_results_table.py to aggregate by experiment.

Usage:
    python generate_scoring_template.py --from results/experiment_outputs.csv --out results/manual_scores.csv
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

SCORE_FIELDS = ["accuracy", "clarity", "groundedness", "notes"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate manual scoring template CSV")
    parser.add_argument(
        "--from",
        dest="source",
        type=Path,
        required=True,
        help="Path to experiment_outputs.csv",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/manual_scores.csv"),
        help="Output CSV path",
    )
    args = parser.parse_args()

    with open(args.source, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise SystemExit("Empty or invalid CSV")
        rows = list(reader)

    # Stable order: experiment_name, then question_id
    def sort_key(r: dict) -> tuple:
        return (r.get("experiment_name", ""), r.get("question_id", ""))

    rows.sort(key=sort_key)

    out_fields = [
        "experiment_name",
        "temperature",
        "top_k",
        "prompt_style",
        "prompt_label",
        "question_id",
        "question",
        *SCORE_FIELDS,
    ]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=out_fields)
        w.writeheader()
        for r in rows:
            w.writerow(
                {
                    "experiment_name": r.get("experiment_name", ""),
                    "temperature": r.get("temperature", ""),
                    "top_k": r.get("top_k", ""),
                    "prompt_style": r.get("prompt_style", ""),
                    "prompt_label": r.get("prompt_label", ""),
                    "question_id": r.get("question_id", ""),
                    "question": r.get("question", ""),
                    "accuracy": "",
                    "clarity": "",
                    "groundedness": "",
                    "notes": "",
                }
            )

    print(f"Wrote {len(rows)} rows to {args.out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
