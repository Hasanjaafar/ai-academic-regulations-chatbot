# -*- coding: utf-8 -*-
"""
Fill missing (experiment_name, question_id) rows in an experiment_outputs CSV
without re-running the whole grid.

Uses the first row per experiment_name as the template for temperature, top_k,
and prompt_style. Expects question ids to match evaluation/test_questions.json.

Usage:
    python repair_experiment_outputs.py --dry-run
    python repair_experiment_outputs.py --input results/experiment_outputs.csv --output results/experiment_outputs.csv

Requires: OPENAI_API_KEY, Chroma DB (same as run_experiments.py).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evaluation.experiment_configs import ExperimentConfig
from evaluation.prompt_templates import build_prompt
from evaluation.rag_pipeline import (
    build_context_block,
    format_retrieved_clauses_csv,
    format_similarity_scores_csv,
    get_collection,
    retrieve,
    similarity_line,
)

load_dotenv(PROJECT_ROOT / ".env")

OPENAI_MODEL = "gpt-4o-mini"
QUESTIONS_PATH = PROJECT_ROOT / "evaluation" / "test_questions.json"


def load_questions(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("test_questions.json must be a JSON array")
    return data


def generate_answer(client: OpenAI, prompt: str, temperature: float) -> str:
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return (resp.choices[0].message.content or "").strip()


def row_to_config(template: dict) -> ExperimentConfig:
    return ExperimentConfig(
        experiment_name=(template["experiment_name"] or "").strip(),
        temperature=float(template["temperature"]),
        top_k=int(template["top_k"]),
        prompt_style=(template["prompt_style"] or "").strip(),
        prompt_label=(template.get("prompt_label") or "").strip(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair incomplete experiment_outputs.csv")
    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_ROOT / "results" / "experiment_outputs.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Defaults to --input (overwrite in place after merge)",
    )
    parser.add_argument(
        "--questions",
        type=Path,
        default=QUESTIONS_PATH,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List missing pairs only; no API calls",
    )
    args = parser.parse_args()
    out_path = args.output or args.input

    with open(args.input, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        existing_rows = list(reader)

    if not fieldnames:
        print("Empty or invalid CSV")
        return 1

    questions = load_questions(args.questions)
    q_by_id = {q["id"]: q["question"].strip() for q in questions}
    all_qids = [q["id"] for q in questions]

    exps = []
    seen = set()
    for r in existing_rows:
        n = (r.get("experiment_name") or "").strip()
        if n and n not in seen:
            seen.add(n)
            exps.append(n)

    templates: dict[str, dict] = {}
    for r in existing_rows:
        n = (r.get("experiment_name") or "").strip()
        if n and n not in templates:
            templates[n] = r

    expected = {(e, qid) for e in exps for qid in all_qids}
    have = {
        ((r.get("experiment_name") or "").strip(), (r.get("question_id") or "").strip())
        for r in existing_rows
    }
    missing = sorted(expected - have, key=lambda x: (x[0], all_qids.index(x[1]) if x[1] in all_qids else x[1]))

    print(f"Input: {args.input.resolve()} | rows: {len(existing_rows)}")
    print(f"Experiments: {exps}")
    print(f"Question ids (from JSON): {len(all_qids)}")
    print(f"Missing pairs: {len(missing)}")
    for pair in missing:
        print(f"  {pair[0]}  {pair[1]}")

    if not missing:
        print("Nothing to repair.")
        return 0

    if args.dry_run:
        return 0

    client = OpenAI()
    collection = get_collection()
    new_rows: list[dict] = []

    for exp_name, qid in missing:
        tmpl = templates.get(exp_name)
        if not tmpl:
            print(f"No template row for {exp_name}; skip")
            continue
        if qid not in q_by_id:
            print(f"Unknown question id {qid}; skip")
            continue
        cfg = row_to_config(tmpl)
        qtext = q_by_id[qid]
        try:
            results = retrieve(collection, qtext, cfg.top_k)
            ctx = build_context_block(results)
            sim_line = similarity_line(results)
            prompt = build_prompt(
                prompt_style=cfg.prompt_style,
                question=qtext,
                context_block=ctx,
                sim_line=sim_line,
            )
            answer = generate_answer(client, prompt, temperature=cfg.temperature)
            clauses_csv = format_retrieved_clauses_csv(results)
            sims_csv = format_similarity_scores_csv(results)
        except Exception as e:
            answer = f"[ERROR] {type(e).__name__}: {e}"
            clauses_csv = ""
            sims_csv = ""

        row = {k: "" for k in fieldnames}
        row.update(
            {
                "experiment_name": cfg.experiment_name,
                "question_id": qid,
                "question": qtext,
                "temperature": cfg.temperature,
                "top_k": cfg.top_k,
                "prompt_style": cfg.prompt_style,
                "retrieved_clauses": clauses_csv,
                "answer": answer,
                "similarity_scores": sims_csv,
            }
        )
        if "prompt_label" in fieldnames:
            row["prompt_label"] = cfg.prompt_label
        new_rows.append(row)
        time.sleep(0.15)

    merged = existing_rows + new_rows

    def sort_key(r: dict) -> tuple:
        e = (r.get("experiment_name") or "").strip()
        qid = (r.get("question_id") or "").strip()
        qi = all_qids.index(qid) if qid in all_qids else 999
        return (exps.index(e) if e in exps else 999, qi)

    merged.sort(key=sort_key)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in merged:
            w.writerow({k: r.get(k, "") for k in fieldnames})

    print(f"Wrote {len(merged)} rows to {out_path.resolve()} ({len(new_rows)} new)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
