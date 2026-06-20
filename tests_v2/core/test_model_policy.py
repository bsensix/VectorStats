"""Tests for pinned release model policy."""

from pathlib import Path

from vectorstats_v2.core.model_policy import (
    can_release_with_model_change,
    validate_model_for_release,
)


def test_unpinned_model_is_rejected() -> None:
    assert validate_model_for_release("experimental-model") is False


def test_pinned_model_is_allowed() -> None:
    assert validate_model_for_release("gpt-4.1-mini") is True


def test_model_change_requires_benchmark_evidence_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    assert can_release_with_model_change("gpt-old", "gpt-new", missing) is False


def test_same_model_does_not_require_benchmark_artifact(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    assert (
        can_release_with_model_change("gpt-4.1-mini", "gpt-4.1-mini", missing) is True
    )
