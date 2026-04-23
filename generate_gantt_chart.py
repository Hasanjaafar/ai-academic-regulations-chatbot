from __future__ import annotations

from datetime import datetime
from pathlib import Path

import matplotlib
import matplotlib.dates as mdates

matplotlib.use("Agg")

import matplotlib.pyplot as plt


TASKS = [
    ("Initial Planning and Legal Chatbot Concept Development", "2025-09-25", "2025-10-31"),
    ("Initial System Development", "2025-11-01", "2025-11-26"),
    ("Project Direction Change (Supervisor Feedback Milestone)", "2025-11-27", "2025-12-10"),
    ("Research and Scope Refinement Phase", "2025-12-11", "2026-02-25"),
    ("Dataset Transition (Westminster Regulations)", "2026-02-26", "2026-03-02"),
    ("Data Preprocessing and Embedding Regeneration", "2026-03-03", "2026-03-15"),
    ("RAG System Integration and Refinement", "2026-03-16", "2026-03-28"),
    ("Experimental Design and Setup", "2026-03-29", "2026-04-05"),
    ("Experiment Execution", "2026-04-06", "2026-04-08"),
    ("Manual Evaluation", "2026-04-09", "2026-04-18"),
    ("Results Analysis and Visualisation", "2026-04-19", "2026-04-21"),
    ("Report Drafting (Initial Writing)", "2026-03-20", "2026-04-10"),
    ("Final Report Writing and Submission", "2026-04-22", "2026-04-23"),
]

COLORS = [
    "#4E79A7",
    "#F28E2B",
    "#E15759",
    "#76B7B2",
    "#59A14F",
    "#EDC948",
    "#B07AA1",
    "#FF9DA7",
]


def main() -> int:
    root = Path(__file__).resolve().parent
    output_path = root / "gantt_chart.pdf"

    plt.style.use("seaborn-v0_8-whitegrid")
    plt.figure(figsize=(16, 10))
    fig, ax = plt.gcf(), plt.gca()

    for idx, (task, start_str, end_str) in enumerate(TASKS):
        start = datetime.strptime(start_str, "%Y-%m-%d")
        end = datetime.strptime(end_str, "%Y-%m-%d")
        duration = (end - start).days + 1
        ax.barh(
            idx,
            duration,
            left=mdates.date2num(start),
            height=0.62,
            color=COLORS[idx % len(COLORS)],
            edgecolor="white",
            linewidth=1.0,
        )

    ax.set_yticks(range(len(TASKS)))
    ax.set_yticklabels([task for task, _, _ in TASKS], fontsize=10)
    ax.invert_yaxis()

    ax.set_title("Project Gantt Chart", fontsize=17, weight="semibold", pad=14)
    ax.set_xlabel("Project Timeline", fontsize=12)

    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right", fontsize=9)

    ax.grid(axis="x", linestyle="--", linewidth=0.7, alpha=0.45)
    ax.grid(axis="y", visible=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#666666")
    ax.spines["bottom"].set_color("#666666")
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    fig.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
