"""Tests for privacy filtering before AI requests."""

from vectorstats_v2.core.privacy_guard import filter_payload_fields, sanitize_for_ai


def test_unknown_fields_are_excluded_by_default() -> None:
    payload = {"email": ["x"], "name": ["Ana"]}
    filtered = filter_payload_fields(payload, allowlist=set())

    assert filtered == {}


def test_geometry_and_pii_are_removed_and_redacted() -> None:
    payload = {"geometry": "POINT(0 0)", "cpf": "123", "name": "A"}
    safe_payload, debug_trace = sanitize_for_ai(payload, allowlist={"name"})

    assert "geometry" not in safe_payload
    assert "cpf" not in safe_payload
    assert safe_payload["name"] == "A"
    assert "[REDACTED]" in debug_trace
