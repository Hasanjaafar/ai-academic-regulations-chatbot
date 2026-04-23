# -*- coding: utf-8 -*-
"""
Aggregate manual scores (per question) into report-ready summary tables.

Reads a filled manual_scores.csv (from generate_scoring_template.py) and writes
mean (optional: std) per experiment_name. Use --markdown to print a table for Word/LaTeX.

Usage:
    python build_results_table.py --scores results/manual_scores.csv --out results/results_summary.csv
    python build_results_table.py --scores results/manual_scores.csv --markdown
"""
from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

METRICS = ("accuracy", "clarity", "groundedness")


def _parse_float(cell: str) -> float | None:
    s = (cell or "").strip()
    if s == "":
        return None
    try:
        return float(s.replace(",", "."))
    except ValueError:
        return None


def _fmt_config(
    temperature: str,
    top_k: str,
    prompt_label: str,
) -> str:
    """Human-readable row label, e.g. 0.2 / k=3 (Prompt A)."""
    t = (temperature or "").strip()
    k = (top_k or "").strip()
    pl = (prompt_label or "").strip()
    base = f"{t} / k={k}" if t or k else ""
    if pl:
        return f"{base} (Prompt {pl})" if base else f"Prompt {pl}"
    return base or "—"


def load_scores(path: Path) -> list[dict[str, Any]]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def warn_duplicate_scores_across_experiments(rows: list[dict[str, Any]]) -> None:
    """
    If every experiment shares the same (accuracy, clarity, groundedness) for each
    question_id, per-experiment means will be identical — usually a scoring mistake
    (copy-paste) rather than an aggregation bug.
    """
    by_q: dict[str, dict[str, tuple[float | None, float | None, float | None]]] = defaultdict(
        dict
    )
    for r in rows:
        qid = (r.get("question_id") or "").strip()
        exp = (r.get("experiment_name") or "").strip()
        if not qid or not exp:
            continue
        triple = tuple(_parse_float(r.get(m, "") or "") for m in METRICS)
        by_q[qid][exp] = triple

    exps = {(r.get("experiment_name") or "").strip() for r in rows}
    exps.discard("")
    if len(exps) <= 1:
        return

    same_for_all_questions = 0
    for qid, ed in by_q.items():
        triples = list(ed.values())
        if len(triples) < 2:
            continue
        if len({t for t in triples}) == 1:
            same_for_all_questions += 1

    nq = len(by_q)
    if nq and same_for_all_questions == nq:
        print(
            "WARNING: For every question_id, all experiments have the same "
            "accuracy/clarity/groundedness triple. Per-experiment means will match "
            "in results_summary.csv. Re-score using each experiment's answers in "
            "phase5_outputs (or your run CSV), not a single copied column."
        )
    elif same_for_all_questions:
        print(
            f"NOTE: {same_for_all_questions}/{nq} question_ids have identical scores "
            "across all experiments; check for copy-paste."
        )


def aggregate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group by experiment_name; mean per metric; count scored rows."""
    groups: dict[str, list[dict[str, Any]]] = {}
    meta: dict[str, dict[str, str]] = {}

    for r in rows:
        name = (r.get("experiment_name") or "").strip()
        if not name:
            continue
        groups.setdefault(name, []).append(r)
        if name not in meta:
            meta[name] = {
                "temperature": (r.get("temperature") or "").strip(),
                "top_k": (r.get("top_k") or "").strip(),
                "prompt_style": (r.get("prompt_style") or "").strip(),
                "prompt_label": (r.get("prompt_label") or "").strip(),
            }

    summaries: list[dict[str, Any]] = []
    for name in sorted(groups.keys()):
        grows = groups[name]
        m = meta.get(name, {})
        per_metric: dict[str, list[float]] = {k: [] for k in METRICS}
        for row in grows:
            for metric in METRICS:
                v = _parse_float(row.get(metric, "") or "")
                if v is not None:
                    per_metric[metric].append(v)

        n_scored = sum(
            1
            for row in grows
            if any(_parse_float(row.get(m, "") or "") is not None for m in METRICS)
        )

        out: dict[str, Any] = {
            "experiment_name": name,
            "config": _fmt_config(m.get("temperature", ""), m.get("top_k", ""), m.get("prompt_label", "")),
            "temperature": m.get("temperature", ""),
            "top_k": m.get("top_k", ""),
            "prompt_style": m.get("prompt_style", ""),
            "prompt_label": m.get("prompt_label", ""),
            "n_rows": len(grows),
            "n_scored": n_scored,
        }
        for metric in METRICS:
            vals = per_metric[metric]
            out[f"mean_{metric}"] = round(statistics.mean(vals), 4) if vals else ""
            out[f"std_{metric}"] = (
                round(statistics.stdev(vals), 4) if len(vals) > 1 else (0.0 if vals else "")
            )
        summaries.append(out)

    return summaries


def write_csv(summaries: list[dict[str, Any]], path: Path) -> None:
    if not summaries:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
        return
    keys = list(summaries[0].keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for s in summaries:
            w.writerow(s)


def markdown_table(summaries: list[dict[str, Any]], include_std: bool) -> str:
    if not summaries:
        return "_No data._\n"
    cols = ["Config", "Accuracy", "Clarity", "Groundedness"]
    if include_std:
        cols = [
            "Config",
            "Accuracy (mean, sd)",
            "Clarity (mean, sd)",
            "Groundedness (mean, sd)",
            "N",
        ]
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for s in summaries:
        cfg = str(s.get("config", ""))
        if include_std:
            def cell(metric: str) -> str:
                mu = s.get(f"mean_{metric}")
                sig = s.get(f"std_{metric}")
                if mu == "" or mu is None:
                    return "—"
                if sig == "" or sig is None or sig == 0.0:
                    return f"{mu}"
                return f"{mu} ({sig})"

            lines.append(
                "| "
                + " | ".join(
                    [
                        cfg,
                        cell("accuracy"),
                        cell("clarity"),
                        cell("groundedness"),
                        str(s.get("n_scored", "")),
                    ]
                )
                + " |"
            )
        else:
            lines.append(
                "| "
                + " | ".join(
                    [
                        cfg,
                        str(s.get("mean_accuracy", "—")),
                        str(s.get("mean_clarity", "—")),
                        str(s.get("mean_groundedness", "—")),
                    ]
                )
                + " |"
            )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build report summary table from manual scores")
    parser.add_argument(
        "--scores",
        type=Path,
        default=Path("results/manual_scores.csv"),
        help="Filled manual_scores.csv",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/results_summary.csv"),
        help="Output aggregated CSV",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Print Markdown table to stdout",
    )
    parser.add_argument(
        "--with-std",
        action="store_true",
        help="In --markdown, show mean±std and N",
    )
    args = parser.parse_args()

    rows = load_scores(args.scores)
    warn_duplicate_scores_across_experiments(rows)
    summaries = aggregate(rows)
    write_csv(summaries, args.out)
    print(f"Wrote {len(summaries)} config rows to {args.out.resolve()}")
    if args.markdown:
        print(markdown_table(summaries, include_std=args.with_std))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
