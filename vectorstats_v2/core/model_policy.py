"""Release model policy and benchmark-evidence guards."""

from __future__ import annotations

from pathlib import Path


PINNED_RELEASE_MODELS = {"gpt-4.1-mini"}


def validate_model_for_release(model_id: str) -> bool:
    return model_id in PINNED_RELEASE_MODELS


def can_release_with_model_change(
    previous_model: str,
    next_model: str,
    benchmark_artifact_path: Path,
) -> bool:
    if previous_model == next_model:
        return validate_model_for_release(next_model)

    if not validate_model_for_release(next_model):
        return False

    return benchmark_artifact_path.exists()


__all__ = [
    "PINNED_RELEASE_MODELS",
    "can_release_with_model_change",
    "validate_model_for_release",
]
