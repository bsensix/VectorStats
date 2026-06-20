"""Tests for OpenAI policy and budget guard behavior."""

from vectorstats_v2.core.openai_client import (
    build_retry_request,
    enforce_release_model,
    compute_retry_plan,
    estimate_cost,
    policy_limits,
    preflight_budget_gate,
    reconcile_cost,
    reserve_cost,
    retries_for_status,
    timeout_policy,
)


def test_retry_budget_caps_total_wait_time() -> None:
    plan = compute_retry_plan(status_code=429)
    assert plan.total_budget_seconds <= 60


def test_timeouts_are_spec_values() -> None:
    policy = timeout_policy()
    assert policy.connect_seconds == 5
    assert policy.response_seconds == 45


def test_retry_matrix_matches_spec() -> None:
    assert len(retries_for_status(429)) == 2
    assert len(retries_for_status(500)) == 2
    assert len(retries_for_status(408)) == 1
    assert len(retries_for_status(401)) == 0


def test_retry_408_uses_reduced_context() -> None:
    retry_request = build_retry_request(
        status_code=408, context={"rows": list(range(1000))}
    )
    assert retry_request["rows_count"] < 1000


def test_cost_policy_limits_are_enforced() -> None:
    limits = policy_limits()
    assert limits.max_input_tokens == 8000
    assert limits.max_output_tokens == 1200
    assert limits.max_retained_turns == 6
    assert limits.soft_budget_usd == 2.0
    assert limits.hard_budget_usd == 5.0


def test_budget_reserve_and_reconcile_flow() -> None:
    ledger = reserve_cost(estimated_usd=0.4, spent_usd=1.7, hard_limit_usd=5.0)
    final_ledger = reconcile_cost(ledger, actual_usd=0.2)
    assert final_ledger.spent_usd == 1.9


def test_pricing_snapshot_metadata_is_required_for_estimation() -> None:
    snapshot = {
        "provider": "openai",
        "model": "gpt-x",
        "price_timestamp": "2026-06-17T00:00:00Z",
    }
    estimate = estimate_cost(
        input_tokens=1000,
        output_tokens=300,
        pricing_snapshot=snapshot,
    )
    assert estimate.provider == "openai"
    assert estimate.price_timestamp == "2026-06-17T00:00:00Z"


def test_precall_reservation_blocks_before_api_when_hard_limit_exceeded() -> None:
    blocked = preflight_budget_gate(
        spent_usd=4.9, estimated_usd=0.3, hard_limit_usd=5.0
    )
    assert blocked is True


def test_release_model_enforcement_uses_pinned_policy() -> None:
    assert enforce_release_model("gpt-4.1-mini") == "gpt-4.1-mini"
