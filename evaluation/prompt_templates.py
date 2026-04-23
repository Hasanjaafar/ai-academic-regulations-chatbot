# -*- coding: utf-8 -*-
"""Prompt styles for RAG evaluation: strict vs semi-flexible vs loose generation."""
from __future__ import annotations

DOCUMENT_SHORT = "Handbook of Academic Regulations 2025–2026"

# Shared structure (all styles use the same section headings for comparable outputs)
_OUTPUT_SKELETON = """
OUTPUT FORMAT — use these exact headings (English):

Answer:
Supporting Regulation:
Additional Notes:
Confidence:
"""

_STRICT_RULES = """
STRICT GROUNDING RULES:
- Use ONLY information supported by the regulation excerpts below. Do not use outside knowledge of UK HE or other universities.
- Every factual claim must tie to a clause number or explicitly state the handbook is silent.
- If excerpts do not answer the question, say so under Supporting Regulation or Additional Notes using precise language (no generic "it is advisable to…").
- Confidence must reflect retrieval quality and whether a specific clause applies.
"""

_SEMI_RULES = """
SEMI-FLEXIBLE RULES:
- Ground your answer primarily in the excerpts below; you may use light paraphrasing for readability.
- Cite clause numbers where possible. If the text is unclear, say what is and is not stated.
- Avoid inventing policies not implied by the excerpts. If unsure, state uncertainty in Additional Notes.
"""

_LOOSE_RULES = """
LOOSE RULES:
- Base your answer on the excerpts below, but you may summarize and connect ideas more freely for clarity.
- Still cite relevant clauses when you rely on them. Do not invent specific university rules that are not in the excerpts.
- If excerpts are off-topic, say so briefly and keep Confidence low.
"""


def _retrieval_block(sim_line: str, context_block: str) -> str:
    return (
        f"Retrieval diagnostics (cosine-style similarity, higher = closer):\n{sim_line}\n\n"
        f"Regulation excerpts:\n{context_block}\n"
    )


def build_prompt(
    *,
    prompt_style: str,
    question: str,
    context_block: str,
    sim_line: str,
) -> str:
    """Build the full user prompt for OpenAI given style and RAG context."""
    body = _retrieval_block(sim_line, context_block)
    intro = (
        f"You are an assistant for the University of Westminster {DOCUMENT_SHORT}. "
        "Reply in English only.\n"
    )

    if prompt_style == "strict":
        rules = _STRICT_RULES
    elif prompt_style == "semi_flexible":
        rules = _SEMI_RULES
    elif prompt_style == "loose":
        rules = _LOOSE_RULES
    else:
        raise ValueError(f"Unknown prompt_style: {prompt_style}")

    return (
        intro
        + rules
        + "\n"
        + _OUTPUT_SKELETON
        + "\nCurrent question:\n"
        + question.strip()
        + "\n\n"
        + body
        + "\nProduce your full structured answer:"
    )
