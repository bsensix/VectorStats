"""Context cache and lifecycle helpers for VectorStats v2."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json

from vectorstats_v2.core.contracts import AnalyticalContext
from vectorstats_v2.core.data_access import normalize_numeric


def context_cache_key(
    layer_id: str,
    selected_fields: list[str],
    filters: dict[str, object],
    selection_mode: str,
    project_uuid: str,
) -> str:
    raw_payload = {
        "layer_id": layer_id,
        "selected_fields": sorted(selected_fields),
        "filters": filters,
        "selection_mode": selection_mode,
        "project_uuid": project_uuid,
    }
    raw = json.dumps(raw_payload, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def should_invalidate(
    previous_state: dict[str, object],
    current_state: dict[str, object],
) -> bool:
    keys = ("layer_id", "selected_fields", "filters", "selection_mode")
    return any(previous_state.get(key) != current_state.get(key) for key in keys)


def should_reuse_context(
    cached_at: datetime,
    now: datetime,
    ttl_seconds: int = 300,
    hard_invalidated: bool = False,
) -> bool:
    if hard_invalidated:
        return False

    age = now - cached_at
    return age <= timedelta(seconds=ttl_seconds)


def build_context(
    layer_id: str,
    selected_fields: list[str],
    filters: dict[str, object],
    selection_mode: str,
    project_uuid: str,
    numeric_values: list[object] | None = None,
) -> AnalyticalContext:
    cache_key = context_cache_key(
        layer_id=layer_id,
        selected_fields=selected_fields,
        filters=filters,
        selection_mode=selection_mode,
        project_uuid=project_uuid,
    )
    normalized_values = normalize_numeric(numeric_values or [])
    count = len(normalized_values)

    summary_stats: dict[str, float | int | None] = {
        "count": count,
        "min": min(normalized_values) if normalized_values else None,
        "max": max(normalized_values) if normalized_values else None,
        "mean": (sum(normalized_values) / count) if count else None,
    }

    sample_rows = [
        {"row_index": idx, "value": value}
        for idx, value in enumerate(normalized_values[:3], start=1)
    ]

    field_profile = {
        "selected_fields": selected_fields,
        "selection_mode": selection_mode,
        "numeric_points": count,
    }

    created_at = datetime.now(timezone.utc).isoformat()
    return AnalyticalContext(
        context_id=cache_key,
        context_version=f"ctx-{cache_key[:12]}",
        layer_id=layer_id,
        selected_fields=selected_fields,
        filters=filters,
        selection_mode=selection_mode,
        summary_stats=summary_stats,
        sample_rows=sample_rows,
        field_profile=field_profile,
        created_at=created_at,
    )


__all__ = [
    "build_context",
    "context_cache_key",
    "should_invalidate",
    "should_reuse_context",
]
