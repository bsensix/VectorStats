"""Privacy filtering rules for AI-bound payloads."""

from __future__ import annotations

DENYLIST_FIELDS = {"cpf", "cnpj", "email", "phone", "document", "address", "geometry"}


def filter_payload_fields(
    payload: dict[str, object],
    allowlist: set[str],
) -> dict[str, object]:
    filtered: dict[str, object] = {}
    for key, value in payload.items():
        if key in DENYLIST_FIELDS:
            continue
        if key not in allowlist:
            continue
        filtered[key] = value
    return filtered


def sanitize_for_ai(
    payload: dict[str, object],
    allowlist: set[str],
) -> tuple[dict[str, object], str]:
    safe_payload = filter_payload_fields(payload, allowlist=allowlist)
    redacted_fields = [key for key in payload if key not in safe_payload]
    if redacted_fields:
        trace = f"suppressed={','.join(sorted(redacted_fields))}; marker=[REDACTED]"
    else:
        trace = "suppressed=none"
    return safe_payload, trace


__all__ = ["DENYLIST_FIELDS", "filter_payload_fields", "sanitize_for_ai"]
