"""Tests for dashboard template engine contracts."""

from vectorstats_v2.core.template_engine import TEMPLATE_IDS, render_template


def test_template_engine_supports_required_templates() -> None:
    assert {"distribution", "category_comparison", "time_series"}.issubset(TEMPLATE_IDS)


def test_render_template_returns_standard_shape() -> None:
    result = render_template(
        template_id="distribution",
        context={"summary_stats": {"count": 3, "mean": 10.0}},
        params={"field": "population"},
    )

    assert result["template_id"] == "distribution"
    assert "metrics" in result
    assert "series" in result
    assert "group_breakdown" in result
    assert "warnings" in result


def test_render_template_raises_for_unknown_template() -> None:
    try:
        render_template(template_id="unknown", context={}, params={})
    except ValueError as exc:
        assert "unknown template" in str(exc).lower()
    else:
        raise AssertionError("render_template should reject unsupported templates")
