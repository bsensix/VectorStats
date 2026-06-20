"""Tests for telemetry payload safeguards."""

from vectorstats_v2.core.telemetry import build_ai_event, build_event


def test_telemetry_never_contains_raw_payload_fields() -> None:
    event = build_event("ai_call", latency_ms=10, raw_payload={"cpf": "123"})

    assert "raw_payload" not in event
    assert event["event"] == "ai_call"
    assert event["latency_ms"] == 10


def test_telemetry_includes_model_prompt_schema_versions() -> None:
    event = build_ai_event(model_id="gpt-x", prompt_version="p1", schema_version="s1")

    assert event["model_id"] == "gpt-x"
    assert event["prompt_version"] == "p1"
    assert event["schema_version"] == "s1"
