from __future__ import annotations

from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


HEADERS = [
    "Test ID",
    "Requirement ID",
    "Test Description",
    "Input",
    "Expected Result",
    "Actual Result",
    "Status",
]

ROWS = [
    [
        "TC01",
        "FR1",
        "Verify that the user can submit a question about the academic regulations through the chatbot interface.",
        "User enters: What happens if coursework is submitted within 24 hours after the deadline?",
        "The question is accepted and passed to the backend processing pipeline.",
        "The submitted question was captured and processed successfully.",
        "Pass",
    ],
    [
        "TC02",
        "FR2",
        "Verify that the system retrieves relevant academic regulation clauses using semantic similarity.",
        "Query about coursework submitted more than 24 hours late without an approved extension.",
        "The retrieval module returns handbook clauses related to late submission and extensions.",
        "Relevant academic regulation clauses were retrieved and ranked for use as context.",
        "Pass",
    ],
    [
        "TC03",
        "FR3",
        "Verify that the system generates an answer using retrieved academic regulation context.",
        "Question about Progression and Award Boards with retrieved handbook clauses supplied to the model.",
        "The generated response explains the board role using the retrieved handbook context.",
        "The response used the retrieved context and gave a coherent explanation of board responsibilities.",
        "Pass",
    ],
    [
        "TC04",
        "FR4",
        "Verify that configurable parameters such as temperature and top-k affect system execution.",
        "Run the same question about mitigating circumstances using different temperature and top-k values.",
        "The selected configuration is applied during retrieval and response generation.",
        "The system executed using the configured temperature and top-k settings.",
        "Pass",
    ],
    [
        "TC05",
        "FR5",
        "Verify that generated answers are displayed clearly in the user interface.",
        "Submit a question about examination lateness and wait for the generated answer.",
        "The answer is shown in a readable format without truncation or layout issues.",
        "The generated answer was displayed clearly in the chatbot interface.",
        "Pass",
    ],
    [
        "TC06",
        "FR6",
        "Verify that outputs can be evaluated using accuracy, clarity, and groundedness.",
        "Evaluate handbook-based answers about RPCL, RPEL, academic appeals, and reasonable adjustments.",
        "The system records evaluation scores and produces summary metrics for each criterion.",
        "Accuracy, clarity, and groundedness scores were recorded and summarized.",
        "Pass",
    ],
]


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = [
        "arialbd.ttf" if bold else "arial.ttf",
        "calibrib.ttf" if bold else "calibri.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
    ]
    for name in names:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _line_height(font: ImageFont.ImageFont) -> int:
    bbox = font.getbbox("Ag")
    return bbox[3] - bbox[1] + 8


def _wrap_cell(text: str, font: ImageFont.ImageFont, width: int) -> list[str]:
    avg_char_width = max(font.getlength("abcdefghijklmnopqrstuvwxyz") / 26, 1)
    max_chars = max(int(width / avg_char_width), 8)
    lines: list[str] = []
    for paragraph in str(text).splitlines() or [""]:
        chunks = wrap(paragraph, width=max_chars, break_long_words=False)
        lines.extend(chunks or [""])
    return lines


def _draw_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    lines: list[str],
    font: ImageFont.ImageFont,
    fill: str,
    line_height: int,
    align: str = "left",
    box_width: int = 0,
) -> None:
    x, y = xy
    for idx, line in enumerate(lines):
        line_x = x
        if align == "center":
            line_width = draw.textlength(line, font=font)
            line_x = x + max((box_width - line_width) / 2, 0)
        draw.text((line_x, y + idx * line_height), line, font=font, fill=fill)


def render(output_path: Path) -> None:
    title_font = _font(42, bold=True)
    header_font = _font(20, bold=True)
    body_font = _font(18)
    body_bold = _font(18, bold=True)

    page_width = 2400
    margin = 42
    title_gap = 36
    header_height = 78
    cell_pad_x = 14
    cell_pad_y = 18
    line_height = _line_height(body_font)

    col_widths = [126, 170, 420, 330, 405, 405, 112]
    table_width = sum(col_widths)

    wrapped_rows: list[list[list[str]]] = []
    row_heights: list[int] = []
    for row in ROWS:
        wrapped = [
            _wrap_cell(cell, body_font, col_widths[i] - 2 * cell_pad_x)
            for i, cell in enumerate(row)
        ]
        wrapped_rows.append(wrapped)
        row_heights.append(max(len(lines) for lines in wrapped) * line_height + 2 * cell_pad_y)

    title_height = title_font.getbbox("Test Coverage Table")[3] + 8
    table_top = margin + title_height + title_gap
    page_height = table_top + header_height + sum(row_heights) + margin
    image = Image.new("RGB", (page_width, page_height), "white")
    draw = ImageDraw.Draw(image)

    title_color = "#1f2933"
    header_color = "#1f4e79"
    stripe_color = "#f6f8fb"
    edge_color = "#d9e1ea"
    text_color = "#111827"
    status_color = "#1b7f4c"

    draw.text((margin, margin), "Test Coverage Table", font=title_font, fill=title_color)

    table_left = margin
    x = table_left
    y = table_top
    for i, header in enumerate(HEADERS):
        w = col_widths[i]
        draw.rectangle([x, y, x + w, y + header_height], fill=header_color, outline=edge_color, width=2)
        header_lines = _wrap_cell(header, header_font, w - 2 * cell_pad_x)
        _draw_text(
            draw,
            (x + cell_pad_x, y + 24),
            header_lines,
            header_font,
            "white",
            _line_height(header_font),
        )
        x += w

    y += header_height
    for row_idx, row in enumerate(wrapped_rows):
        row_height = row_heights[row_idx]
        x = table_left
        fill = stripe_color if row_idx % 2 else "white"
        for col_idx, lines in enumerate(row):
            w = col_widths[col_idx]
            draw.rectangle([x, y, x + w, y + row_height], fill=fill, outline=edge_color, width=2)
            font = body_bold if col_idx in {0, 1, 6} else body_font
            color = status_color if col_idx == 6 else text_color
            align = "center" if col_idx in {0, 1, 6} else "left"
            content_height = len(lines) * line_height
            text_y = y + max((row_height - content_height) // 2, cell_pad_y)
            _draw_text(
                draw,
                (x + cell_pad_x, text_y),
                lines,
                font,
                color,
                line_height,
                align=align,
                box_width=w - 2 * cell_pad_x,
            )
            x += w
        y += row_height

    # Trim extra right-side whitespace while retaining a clean page margin.
    image = image.crop((0, 0, table_left + table_width + margin, page_height))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)


def main() -> int:
    output = Path("results") / "test_coverage_table.png"
    render(output)
    print(output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
