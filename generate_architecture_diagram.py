from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


TITLE = "High-Level System Architecture"
OUTPUT_NAME = "high_level_system_architecture.png"


def add_box(ax, xy: tuple[float, float], width: float, height: float, text: str, *,
            facecolor: str = "#F7F8FA", edgecolor: str = "#4A4F57") -> tuple[float, float, float, float]:
    x, y = xy
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.02,rounding_size=0.04",
        linewidth=1.4,
        edgecolor=edgecolor,
        facecolor=facecolor,
    )
    ax.add_patch(patch)
    ax.text(
        x + width / 2,
        y + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=11,
        color="#1F2933",
        wrap=True,
    )
    return x, y, width, height


def add_arrow(ax, start: tuple[float, float], end: tuple[float, float]) -> None:
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=15,
        linewidth=1.4,
        color="#5B6470",
        shrinkA=4,
        shrinkB=4,
    )
    ax.add_patch(arrow)


def main() -> int:
    root = Path(__file__).resolve().parent
    output_path = root / OUTPUT_NAME

    fig, ax = plt.subplots(figsize=(16, 9), facecolor="white")
    ax.set_facecolor("white")
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis("off")

    fig.suptitle(TITLE, fontsize=18, fontweight="semibold", y=0.96, color="#1F2933")

    top_y = 7.0
    bottom_y = 3.0
    box_w = 1.75
    box_h = 1.0

    top_boxes = [
        add_box(ax, (0.6, top_y), box_w, box_h, "User"),
        add_box(ax, (2.5, top_y), box_w, box_h, "Streamlit UI"),
        add_box(ax, (4.4, top_y), box_w, box_h, "Query\nProcessing"),
        add_box(ax, (6.3, top_y), box_w, box_h, "Embedding\nModel"),
        add_box(ax, (8.2, top_y), box_w, box_h, "ChromaDB\nRetrieval"),
        add_box(ax, (10.1, top_y), box_w, box_h, "Top-k Relevant\nClauses"),
    ]

    bottom_boxes = [
        add_box(ax, (6.3, bottom_y), box_w, box_h, "Prompt\nBuilder"),
        add_box(ax, (8.2, bottom_y), box_w, box_h, "OpenAI LLM"),
        add_box(ax, (10.1, bottom_y), box_w, box_h, "Generated\nResponse"),
        add_box(ax, (12.0, bottom_y), box_w, box_h, "Display in UI"),
    ]

    for left_box, right_box in zip(top_boxes, top_boxes[1:]):
        add_arrow(
            ax,
            (left_box[0] + left_box[2], left_box[1] + left_box[3] / 2),
            (right_box[0], right_box[1] + right_box[3] / 2),
        )

    add_arrow(ax, (11.85, 7.0), (7.2, 4.05))

    for left_box, right_box in zip(bottom_boxes, bottom_boxes[1:]):
        add_arrow(
            ax,
            (left_box[0] + left_box[2], left_box[1] + left_box[3] / 2),
            (right_box[0], right_box[1] + right_box[3] / 2),
        )

    add_arrow(ax, (13.75, 3.5), (13.75, 6.6))
    add_arrow(ax, (13.75, 7.0), (4.2, 7.0))

    ax.text(
        8.0,
        1.25,
        "Flow: Retrieval-augmented generation pipeline from user query to grounded response",
        ha="center",
        va="center",
        fontsize=10,
        color="#5B6470",
    )

    fig.tight_layout(rect=(0.02, 0.04, 0.98, 0.93))
    fig.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    print(f"Saved {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
