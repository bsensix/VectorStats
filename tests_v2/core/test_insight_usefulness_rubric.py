"""Release gate tests for usefulness rubric scoring."""

from vectorstats_v2.core.insight_formatter import (
    passes_usefulness_rubric,
    usefulness_score,
)


def test_usefulness_rubric_requires_3_of_4() -> None:
    flags = {
        "data_backed_finding": True,
        "practical_risk": True,
        "concrete_action": True,
        "layer_specific_language": False,
    }

    assert usefulness_score(flags) >= 3
    assert passes_usefulness_rubric(flags) is True


def test_usefulness_rubric_fails_below_threshold() -> None:
    flags = {
        "data_backed_finding": True,
        "practical_risk": False,
        "concrete_action": True,
        "layer_specific_language": False,
    }

    assert usefulness_score(flags) < 3
    assert passes_usefulness_rubric(flags) is False
