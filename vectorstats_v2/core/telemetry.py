"""Telemetry event builders for local diagnostics."""

from __future__ import annotations

from datetime import datetime, timezone


def build_event(
    event: str,
    latency_ms: int,
    raw_payload: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "event": event,
        "latency_ms": latency_ms,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "raw_payload_size": len(raw_payload or {}),
    }


def build_ai_event(
    model_id: str,
    prompt_version: str,
    schema_version: str,
) -> dict[str, str]:
    return {
        "model_id": model_id,
        "prompt_version": prompt_version,
        "schema_version": schema_version,
    }


__all__ = ["build_event", "build_ai_event"]
