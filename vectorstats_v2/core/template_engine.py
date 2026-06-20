"""Template registry and rendering helpers for Dashboard tab."""

from __future__ import annotations

TEMPLATE_IDS = {"distribution", "category_comparison", "time_series"}


def render_template(
    template_id: str,
    context: dict[str, object],
    params: dict[str, object],
) -> dict[str, object]:
    if template_id not in TEMPLATE_IDS:
        raise ValueError(f"Unknown template: {template_id}")

    raw_summary_stats = context.get("summary_stats", {})
    summary_stats = raw_summary_stats if isinstance(raw_summary_stats, dict) else {}
    return {
        "template_id": template_id,
        "metrics": {
            "count": summary_stats.get("count", 0),
            "mean": summary_stats.get("mean"),
        },
        "series": [],
        "group_breakdown": {},
        "warnings": [],
        "params": dict(params),
    }


__all__ = ["TEMPLATE_IDS", "render_template"]
