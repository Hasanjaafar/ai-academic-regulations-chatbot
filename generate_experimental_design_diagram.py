from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


TITLE = "Experimental Design and Evaluation Framework"
OUTPUT_NAME = "experimental_design_framework.png"


def add_box(
    ax,
    xy: tuple[float, float],
    width: float,
    height: float,
    text: str,
    *,
    facecolor: str = "#F7F9FC",
    edgecolor: str = "#5A6778",
    fontsize: int = 11,
    weight: str = "normal",
) -> tuple[float, float, float, float]:
    x, y = xy
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        linewidth=1.5,
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
        fontsize=fontsize,
        fontweight=weight,
        color="#1F2933",
        wrap=True,
    )
    return x, y, width, height


def add_group(
    ax,
    xy: tuple[float, float],
    width: float,
    height: float,
    label: str,
    *,
    edgecolor: str = "#8A97A6",
    facecolor: str = "#FBFCFE",
) -> tuple[float, float, float, float]:
    x, y = xy
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.03,rounding_size=0.04",
        linewidth=1.6,
        linestyle="-",
        edgecolor=edgecolor,
        facecolor=facecolor,
    )
    ax.add_patch(patch)
    ax.text(
        x + 0.18,
        y + height - 0.24,
        label,
        ha="left",
        va="top",
        fontsize=12,
        fontweight="semibold",
        color="#334155",
    )
    return x, y, width, height


def add_arrow(
    ax,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    color: str = "#5B6470",
    linewidth: float = 1.6,
) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=16,
            linewidth=linewidth,
            color=color,
            shrinkA=5,
            shrinkB=5,
            connectionstyle="arc3",
        )
    )


def add_table(ax, xy: tuple[float, float], width: float, height: float) -> tuple[float, float, float, float]:
    x, y = xy
    add_box(
        ax,
        (x, y),
        width,
        height,
        "",
        facecolor="#F4F8F4",
        edgecolor="#5E7D66",
        fontsize=12,
        weight="semibold",
    )

    ax.text(
        x + width / 2,
        y + height * 0.9,
        "Summary Table",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="semibold",
        color="#2F3B34",
    )

    header_y = y + height * 0.65
    row_y = y + height * 0.35
    ax.plot([x + width * 0.32, x + width * 0.32], [y + 0.12, y + height - 0.12], color="#8FA39A", lw=1.0)
    ax.plot([x + width * 0.63, x + width * 0.63], [y + 0.12, y + height - 0.12], color="#8FA39A", lw=1.0)
    ax.plot([x + 0.12, x + width - 0.12], [header_y, header_y], color="#8FA39A", lw=1.0)
    ax.plot([x + 0.12, x + width - 0.12], [row_y, row_y], color="#D2DBD5", lw=0.9)

    ax.text(x + width * 0.16, y + height * 0.78, "Config", ha="center", va="center", fontsize=9, color="#2F3B34")
    ax.text(x + width * 0.475, y + height * 0.78, "Metric", ha="center", va="center", fontsize=9, color="#2F3B34")
    ax.text(x + width * 0.815, y + height * 0.78, "Score", ha="center", va="center", fontsize=9, color="#2F3B34")

    ax.text(x + width * 0.16, y + height * 0.50, "C1", ha="center", va="center", fontsize=9, color="#475569")
    ax.text(x + width * 0.475, y + height * 0.50, "Accuracy", ha="center", va="center", fontsize=9, color="#475569")
    ax.text(x + width * 0.815, y + height * 0.50, "4.2", ha="center", va="center", fontsize=9, color="#475569")

    ax.text(x + width * 0.16, y + height * 0.22, "C2", ha="center", va="center", fontsize=9, color="#475569")
    ax.text(x + width * 0.475, y + height * 0.22, "Clarity", ha="center", va="center", fontsize=9, color="#475569")
    ax.text(x + width * 0.815, y + height * 0.22, "4.5", ha="center", va="center", fontsize=9, color="#475569")
    return x, y, width, height


def main() -> int:
    root = Path(__file__).resolve().parent
    output_path = root / OUTPUT_NAME

    fig, ax = plt.subplots(figsize=(18, 10), facecolor="white")
    ax.set_facecolor("white")
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 10)
    ax.axis("off")

    fig.suptitle(TITLE, fontsize=19, fontweight="semibold", y=0.97, color="#1F2933")

    fixed = add_box(
        ax,
        (0.5, 4.2),
        2.2,
        1.2,
        "Fixed Question Set",
        facecolor="#EEF4FB",
        edgecolor="#5C7DA5",
        fontsize=12,
        weight="semibold",
    )

    config_group = add_group(ax, (3.2, 2.2), 5.4, 5.2, "Configurations", edgecolor="#8EA3B8", facecolor="#F9FBFD")
    temperature = add_box(ax, (3.7, 5.7), 1.35, 0.95, "Temperature\n0.0-1.0", facecolor="#F3F7FC", edgecolor="#6D89A6")
    topk = add_box(ax, (5.25, 5.7), 1.35, 0.95, "Top-k\nRetrieval", facecolor="#F3F7FC", edgecolor="#6D89A6")
    prompt_a = add_box(ax, (6.8, 5.7), 1.35, 0.95, "Prompt\nStyle A", facecolor="#F3F7FC", edgecolor="#6D89A6")
    prompt_b = add_box(ax, (4.5, 4.15), 1.35, 0.95, "Prompt\nStyle B", facecolor="#F3F7FC", edgecolor="#6D89A6")
    prompt_c = add_box(ax, (6.05, 4.15), 1.35, 0.95, "Prompt\nStyle C", facecolor="#F3F7FC", edgecolor="#6D89A6")
    config_hub = add_box(
        ax,
        (5.0, 2.9),
        1.8,
        0.95,
        "Configuration\nCombinations",
        facecolor="#EAF1F8",
        edgecolor="#6D89A6",
        fontsize=10,
        weight="semibold",
    )

    generated = add_box(
        ax,
        (9.2, 4.2),
        2.1,
        1.2,
        "Generated Responses",
        facecolor="#F6F8FA",
        edgecolor="#6A7280",
        fontsize=12,
        weight="semibold",
    )

    scoring_group = add_group(ax, (11.8, 1.8), 4.2, 5.9, "Manual Scoring", edgecolor="#90A890", facecolor="#FBFDFB")
    scoring_core = add_box(
        ax,
        (12.95, 5.8),
        1.9,
        0.95,
        "Scoring Process",
        facecolor="#EFF7EF",
        edgecolor="#6E8C72",
        fontsize=11,
        weight="semibold",
    )
    accuracy = add_box(ax, (12.2, 4.1), 1.2, 0.9, "Accuracy", facecolor="#F6FBF6", edgecolor="#6E8C72")
    clarity = add_box(ax, (13.3, 3.0), 1.2, 0.9, "Clarity", facecolor="#F6FBF6", edgecolor="#6E8C72")
    grounded = add_box(ax, (14.4, 4.1), 1.2, 0.9, "Groundedness", facecolor="#F6FBF6", edgecolor="#6E8C72", fontsize=10)

    scores = add_box(
        ax,
        (12.85, 2.0),
        2.1,
        0.9,
        "Aggregated Scores",
        facecolor="#EDF6EE",
        edgecolor="#6E8C72",
        fontsize=11,
        weight="semibold",
    )

    summary = add_table(ax, (4.4, 0.55), 2.8, 1.25)

    analysis = add_box(
        ax,
        (8.3, 0.45),
        4.0,
        1.45,
        "Results Analysis\nStatistical comparison, visualisation,\nand interpretation of findings",
        facecolor="#F4F6FB",
        edgecolor="#6F7EA0",
        fontsize=11,
        weight="semibold",
    )

    add_arrow(ax, (2.7, 4.8), (3.2, 4.8))
    for source in (temperature, topk, prompt_a, prompt_b, prompt_c):
        add_arrow(
            ax,
            (source[0] + source[2] / 2, source[1]),
            (config_hub[0] + config_hub[2] / 2, config_hub[1] + config_hub[3]),
            color="#6B7F94",
        )

    add_arrow(ax, (8.6, 4.8), (9.2, 4.8))
    add_arrow(ax, (11.3, 4.8), (11.8, 4.8))
    add_arrow(ax, (13.9, 5.8), (13.9, 5.0), color="#6E8C72")
    add_arrow(ax, (13.9, 5.8), (12.8, 5.0), color="#6E8C72")
    add_arrow(ax, (13.9, 5.8), (15.0, 5.0), color="#6E8C72")
    add_arrow(ax, (12.8, 4.1), (13.9, 2.9), color="#6E8C72")
    add_arrow(ax, (13.9, 3.0), (13.9, 2.9), color="#6E8C72")
    add_arrow(ax, (15.0, 4.1), (13.9, 2.9), color="#6E8C72")
    add_arrow(ax, (12.85, 2.0), (7.2, 1.15), color="#6E7B7A")
    add_arrow(ax, (7.2, 1.15), (8.3, 1.15), color="#6E7B7A")

    ax.text(
        10.25,
        8.55,
        "All experiments use the same fixed question set\nwhile varying retrieval and prompt configurations.",
        ha="center",
        va="center",
        fontsize=10,
        color="#5B6470",
    )

    ax.text(
        10.2,
        9.15,
        "Methodology flow",
        ha="center",
        va="center",
        fontsize=11,
        fontweight="semibold",
        color="#334155",
    )

    fig.tight_layout(rect=(0.02, 0.03, 0.98, 0.95))
    fig.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    print(f"Saved {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
