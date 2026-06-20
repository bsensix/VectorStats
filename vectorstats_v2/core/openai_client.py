"""Policy helpers for OpenAI request handling in VectorStats v2."""

from __future__ import annotations

from dataclasses import dataclass

from vectorstats_v2.core.model_policy import validate_model_for_release


@dataclass(frozen=True)
class TimeoutPolicy:
    connect_seconds: int
    response_seconds: int


@dataclass(frozen=True)
class RetryPlan:
    delays_seconds: list[float]
    total_budget_seconds: float


@dataclass(frozen=True)
class PolicyLimits:
    max_input_tokens: int
    max_output_tokens: int
    max_retained_turns: int
    soft_budget_usd: float
    hard_budget_usd: float


@dataclass(frozen=True)
class BudgetLedger:
    spent_usd: float
    reserved_usd: float


@dataclass(frozen=True)
class CostEstimate:
    provider: str
    model: str
    price_timestamp: str
    estimated_usd: float


def timeout_policy() -> TimeoutPolicy:
    return TimeoutPolicy(connect_seconds=5, response_seconds=45)


def retries_for_status(status_code: int) -> list[float]:
    if status_code in {429, 500, 502, 503, 504}:
        return [1.0, 3.0]
    if status_code == 408:
        return [1.0]
    return []


def compute_retry_plan(status_code: int) -> RetryPlan:
    delays = retries_for_status(status_code)
    total = min(sum(delays), 60.0)
    return RetryPlan(delays_seconds=delays, total_budget_seconds=total)


def build_retry_request(
    status_code: int, context: dict[str, object]
) -> dict[str, object]:
    rows = context.get("rows", [])
    if not isinstance(rows, list):
        rows = []

    if status_code == 408:
        reduced_rows = rows[: max(1, len(rows) // 4)]
    else:
        reduced_rows = rows

    return {
        "rows": reduced_rows,
        "rows_count": len(reduced_rows),
    }


def policy_limits() -> PolicyLimits:
    return PolicyLimits(
        max_input_tokens=8000,
        max_output_tokens=1200,
        max_retained_turns=6,
        soft_budget_usd=2.0,
        hard_budget_usd=5.0,
    )


def reserve_cost(
    estimated_usd: float, spent_usd: float, hard_limit_usd: float
) -> BudgetLedger:
    if spent_usd + estimated_usd > hard_limit_usd:
        return BudgetLedger(spent_usd=spent_usd, reserved_usd=0.0)
    return BudgetLedger(spent_usd=spent_usd, reserved_usd=estimated_usd)


def reconcile_cost(ledger: BudgetLedger, actual_usd: float) -> BudgetLedger:
    return BudgetLedger(spent_usd=ledger.spent_usd + actual_usd, reserved_usd=0.0)


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    pricing_snapshot: dict[str, str],
) -> CostEstimate:
    input_rate = 0.0000002
    output_rate = 0.0000006
    estimated = (input_tokens * input_rate) + (output_tokens * output_rate)

    return CostEstimate(
        provider=pricing_snapshot["provider"],
        model=pricing_snapshot["model"],
        price_timestamp=pricing_snapshot["price_timestamp"],
        estimated_usd=estimated,
    )


def preflight_budget_gate(
    spent_usd: float, estimated_usd: float, hard_limit_usd: float
) -> bool:
    return spent_usd + estimated_usd > hard_limit_usd


def fallback_insight(summary_stats: dict[str, object]) -> str:
    return f"Diagnostic: local summary only. Count={summary_stats.get('count', 0)}"


def enforce_release_model(model_id: str) -> str:
    if not validate_model_for_release(model_id):
        raise ValueError("Model is not pinned for release")
    return model_id


__all__ = [
    "BudgetLedger",
    "CostEstimate",
    "PolicyLimits",
    "RetryPlan",
    "TimeoutPolicy",
    "build_retry_request",
    "compute_retry_plan",
    "estimate_cost",
    "enforce_release_model",
    "fallback_insight",
    "policy_limits",
    "preflight_budget_gate",
    "reconcile_cost",
    "reserve_cost",
    "retries_for_status",
    "timeout_policy",
]
