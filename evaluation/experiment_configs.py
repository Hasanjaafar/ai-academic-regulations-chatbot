# -*- coding: utf-8 -*-
"""Experiment grid: vary temperature, top_k, and prompt_style. Easy to edit or extend."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product


# Thesis-style prompt labels map to template families in prompt_templates.py
PROMPT_LABEL_TO_STYLE: dict[str, str] = {
    "A": "strict",
    "B": "semi_flexible",
    "C": "loose",
}


@dataclass(frozen=True)
class ExperimentConfig:
    experiment_name: str
    temperature: float
    top_k: int
    prompt_style: str  # strict | semi_flexible | loose
    prompt_label: str = ""  # e.g. A/B/C for thesis tables; optional


def default_configs() -> list[ExperimentConfig]:
    temps = [0.0, 0.4, 0.8]
    top_ks = [3, 5]
    styles = ["strict", "semi_flexible", "loose"]
    out: list[ExperimentConfig] = []
    for t, k, s in product(temps, top_ks, styles):
        name = f"t{t:g}_k{k}_{s}"
        out.append(
            ExperimentConfig(
                experiment_name=name,
                temperature=float(t),
                top_k=int(k),
                prompt_style=s,
            )
        )
    return out


def phase5_configs() -> list[ExperimentConfig]:
    
    specs: list[tuple[str, float, int, str]] = [
        ("exp01", 0.2, 3, "A"),
        ("exp02", 0.2, 5, "A"),
        ("exp03", 0.5, 5, "A"),
        ("exp04", 0.8, 5, "A"),
        ("exp05", 0.5, 3, "B"),
        ("exp06", 0.5, 7, "C"),
    ]
    out: list[ExperimentConfig] = []
    for name, t, k, label in specs:
        style = PROMPT_LABEL_TO_STYLE[label]
        out.append(
            ExperimentConfig(
                experiment_name=name,
                temperature=float(t),
                top_k=int(k),
                prompt_style=style,
                prompt_label=label,
            )
        )
    return out


def minimal_configs() -> list[ExperimentConfig]:
    """Smaller set for quick pilot runs."""
    return [
        ExperimentConfig("pilot_strict", 0.0, 3, "strict"),
        ExperimentConfig("pilot_semi", 0.4, 5, "semi_flexible"),
        ExperimentConfig("pilot_loose", 0.8, 5, "loose"),
    ]
