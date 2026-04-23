# -*- coding: utf-8 -*-
"""
Run handbook RAG experiments: sweep temperature, top_k, and prompt_style over a fixed question set.

Usage (from project root):
    python run_experiments.py
    python run_experiments.py --minimal        # 3 configs only
    python run_experiments.py --phase5         # Phase 5 thesis design (6 configs)
    python run_experiments.py --limit 2        # first 2 questions only (smoke test)

Requires: OPENAI_API_KEY, Chroma DB at data/chroma_db_handbook, collection academic_handbook_2025_26
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

from evaluation.experiment_configs import (
    ExperimentConfig,
    default_configs,
    minimal_configs,
    phase5_configs,
)
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
RESULTS_DIR = PROJECT_ROOT / "results"
OUTPUT_CSV = RESULTS_DIR / "experiment_outputs.csv"
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


def run(
    configs: list[ExperimentConfig],
    questions: list[dict],
    output_path: Path,
) -> int:
    client = OpenAI()
    collection = get_collection()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "experiment_name",
        "question_id",
        "question",
        "temperature",
        "top_k",
        "prompt_style",
        "prompt_label",
        "retrieved_clauses",
        "answer",
        "similarity_scores",
    ]

    rows_written = 0
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for cfg in configs:
            for q in questions:
                qid = q["id"]
                qtext = q["question"].strip()
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
                    answer = generate_answer(
                        client, prompt, temperature=cfg.temperature
                    )
                    clauses_csv = format_retrieved_clauses_csv(results)
                    sims_csv = format_similarity_scores_csv(results)
                except Exception as e:
                    answer = f"[ERROR] {type(e).__name__}: {e}"
                    clauses_csv = ""
                    sims_csv = ""

                writer.writerow(
                    {
                        "experiment_name": cfg.experiment_name,
                        "question_id": qid,
                        "question": qtext,
                        "temperature": cfg.temperature,
                        "top_k": cfg.top_k,
                        "prompt_style": cfg.prompt_style,
                        "prompt_label": cfg.prompt_label,
                        "retrieved_clauses": clauses_csv,
                        "answer": answer,
                        "similarity_scores": sims_csv,
                    }
                )
                rows_written += 1
                f.flush()
                time.sleep(0.15)

    print(f"Wrote {rows_written} rows to {output_path.resolve()}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run RAG evaluation experiments")
    parser.add_argument(
        "--minimal",
        action="store_true",
        help="Use 3 pilot configs instead of full grid",
    )
    parser.add_argument(
        "--phase5",
        action="store_true",
        help="Use Phase 5 fixed design (6 exps: temps 0.2/0.5/0.8, k 3/5/7, prompts A/B/C)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Only first N questions (for smoke tests)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_CSV,
        help="Output CSV path",
    )
    parser.add_argument(
        "--questions",
        type=Path,
        default=QUESTIONS_PATH,
        help="Path to test_questions.json",
    )
    args = parser.parse_args()

    if args.phase5 and args.minimal:
        parser.error("Use only one of --phase5 or --minimal")
    if args.phase5:
        configs = phase5_configs()
    elif args.minimal:
        configs = minimal_configs()
    else:
        configs = default_configs()
    questions = load_questions(args.questions)
    if args.limit is not None:
        questions = questions[: max(0, args.limit)]

    print(
        f"Configs: {len(configs)} | Questions: {len(questions)} | "
        f"Total runs: {len(configs) * len(questions)}"
    )
    return run(configs, questions, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
