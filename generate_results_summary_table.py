from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _num(value: str) -> float | None:
    value = (value or "").strip()
    if not value:
        return None
    return float(value)


def _mean(row: dict[str, str], metric: str) -> str:
    mean = _num(row.get(f"mean_{metric}", ""))
    if mean is None:
        return "-"
    return f"{mean:.2f}"


def load_table(csv_path: Path) -> tuple[list[str], list[list[str]]]:
    with csv_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"No rows found in {csv_path}")

    headers = [
        "Experiment",
        "Configuration",
        "Accuracy",
        "Clarity",
        "Groundedness",
        "N",
    ]
    table_rows = [
        [
            row.get("experiment_name", ""),
            row.get("config", ""),
            _mean(row, "accuracy"),
            _mean(row, "clarity"),
            _mean(row, "groundedness"),
            row.get("n_scored", ""),
        ]
        for row in rows
    ]
    return headers, table_rows


def render_table(csv_path: Path, output_path: Path, title: str) -> None:
    headers, rows = load_table(csv_path)

    fig_width = 12
    fig_height = 1.35 + (len(rows) + 1) * 0.46
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis("off")

    ax.text(
        0.0,
        1.05,
        title,
        transform=ax.transAxes,
        fontsize=16,
        fontweight="bold",
        va="bottom",
        ha="left",
        color="#1f2933",
    )

    table = ax.table(
        cellText=rows,
        colLabels=headers,
        loc="upper left",
        cellLoc="left",
        colLoc="left",
        colWidths=[0.12, 0.30, 0.16, 0.14, 0.18, 0.06],
        bbox=[0.0, 0.0, 1.0, 0.92],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10.5)

    header_color = "#1f4e79"
    stripe_color = "#f5f8fb"
    edge_color = "#d7dee8"

    for (row_idx, col_idx), cell in table.get_celld().items():
        cell.set_edgecolor(edge_color)
        cell.set_linewidth(0.8)
        cell.PAD = 0.08
        if row_idx == 0:
            cell.set_facecolor(header_color)
            cell.set_text_props(color="white", weight="bold")
        elif row_idx % 2 == 0:
            cell.set_facecolor(stripe_color)
        else:
            cell.set_facecolor("white")

        if row_idx > 0 and col_idx in {2, 3, 4, 5}:
            cell.set_text_props(ha="center")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render results_summary.csv as a PNG table")
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("results") / "results_summary.csv",
        help="Input results_summary.csv path",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results") / "results_summary_table.png",
        help="Output PNG path",
    )
    parser.add_argument("--title", default="Results Summary")
    args = parser.parse_args()

    render_table(args.csv, args.out, args.title)
    print(args.out.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
