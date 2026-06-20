"""Tests for context lifecycle and analytical context payload."""

from datetime import datetime, timedelta

import pytest

from vectorstats_v2.core.context_builder import (
    build_context,
    context_cache_key,
    should_invalidate,
    should_reuse_context,
)
from vectorstats_v2.core.contracts import AnalyticalContext
from vectorstats_v2.core.session_state import SessionState


def test_cache_key_changes_when_filters_change() -> None:
    key_one = context_cache_key(
        layer_id="layer_1",
        selected_fields=["population"],
        filters={"min": 1},
        selection_mode="all",
        project_uuid="project-a",
    )
    key_two = context_cache_key(
        layer_id="layer_1",
        selected_fields=["population"],
        filters={"min": 2},
        selection_mode="all",
        project_uuid="project-a",
    )

    assert key_one != key_two


def test_context_invalidates_on_active_layer_change() -> None:
    old_state = {
        "layer_id": "layer_1",
        "selected_fields": ["population"],
        "filters": {},
        "selection_mode": "all",
    }
    new_state = {**old_state, "layer_id": "layer_2"}

    assert should_invalidate(old_state, new_state) is True


def test_context_invalidates_on_selected_fields_change() -> None:
    old_state = {
        "layer_id": "layer_1",
        "selected_fields": ["population"],
        "filters": {},
        "selection_mode": "all",
    }
    new_state = {**old_state, "selected_fields": ["income"]}

    assert should_invalidate(old_state, new_state) is True


def test_context_invalidates_on_selection_mode_change() -> None:
    old_state = {
        "layer_id": "layer_1",
        "selected_fields": ["population"],
        "filters": {},
        "selection_mode": "all",
    }
    new_state = {**old_state, "selection_mode": "selected"}

    assert should_invalidate(old_state, new_state) is True


def test_context_hard_invalidates_on_feature_edit_commit_event() -> None:
    session_state = SessionState()

    assert session_state.hard_invalidated is False
    session_state.on_edit_committed()
    assert session_state.hard_invalidated is True


def test_soft_ttl_reuses_context_when_not_expired() -> None:
    now = datetime(2026, 6, 17, 10, 0, 0)
    cached_at = now - timedelta(minutes=4, seconds=59)

    assert (
        should_reuse_context(cached_at, now, ttl_seconds=300, hard_invalidated=False)
        is True
    )


def test_context_payload_contains_required_fields() -> None:
    context = build_context(
        layer_id="layer_1",
        selected_fields=["population"],
        filters={"city": "Recife"},
        selection_mode="all",
        project_uuid="project-a",
        numeric_values=[100.0, 110.0, 90.0],
    )

    assert isinstance(context, AnalyticalContext)
    assert bool(context.context_id)
    assert context.context_version.startswith("ctx-")
    assert context.sample_rows
    assert context.field_profile
    assert context.created_at


def test_analytical_context_rejects_invalid_context_version_prefix() -> None:
    with pytest.raises(ValueError, match="context_version must start with 'ctx-'"):
        AnalyticalContext(
            context_id="bad-context",
            context_version="v2",
            layer_id="layer_1",
            selected_fields=["population"],
            filters={},
            selection_mode="all",
            summary_stats={},
            sample_rows=[],
            field_profile={},
            created_at="2026-06-17T10:00:00+00:00",
        )
