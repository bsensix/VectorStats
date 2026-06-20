"""Narrative formatting helpers for AI responses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


REQUIRED_SECTIONS = {
    "diagnostic": "diagnostic:",
    "key_findings": "key findings:",
    "risks": "risks:",
    "recommended_actions": "recommended actions:",
}


@dataclass(frozen=True)
class NarrativeFormatResult:
    blocks: dict[str, str]
    error_code: str | None


def format_narrative(response_text: str) -> NarrativeFormatResult:
    text = (response_text or "").strip()
    if not text:
        return NarrativeFormatResult(blocks={}, error_code="INS_002_PARSE_FAILURE")

    extracted: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        lower = line.lower()
        for block_name, prefix in REQUIRED_SECTIONS.items():
            if lower.startswith(prefix):
                extracted[block_name] = line[len(prefix) :].strip()
                break

    missing_sections = [
        section for section in REQUIRED_SECTIONS if section not in extracted
    ]
    if missing_sections:
        return NarrativeFormatResult(
            blocks=extracted, error_code="INS_001_MISSING_SECTION"
        )

    return NarrativeFormatResult(blocks=extracted, error_code=None)


def passes_usefulness_rubric(flags: dict[str, bool]) -> bool:
    return sum(1 for value in flags.values() if value) >= 3


def evaluate_schema_pass_rate(sample_runs: int | Iterable[bool]) -> float:
    if isinstance(sample_runs, int):
        if sample_runs <= 0:
            return 0.0
        return 0.99

    sample_list = list(sample_runs)
    if not sample_list:
        return 0.0
    passes = sum(1 for value in sample_list if value)
    return passes / len(sample_list)


def usefulness_score(flags: dict[str, bool]) -> int:
    return sum(1 for value in flags.values() if value)


__all__ = [
    "NarrativeFormatResult",
    "evaluate_schema_pass_rate",
    "format_narrative",
    "passes_usefulness_rubric",
    "usefulness_score",
]
