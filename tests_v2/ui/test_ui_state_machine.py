"""Tests for Dashboard and Agent controller state transitions."""

from vectorstats_v2.ui.agent_controller import AgentController
from vectorstats_v2.ui.dashboard_controller import DashboardController


def test_agent_controller_blocks_when_context_missing() -> None:
    controller = AgentController(session_state={})

    result = controller.on_ask("show me insights")

    assert result["state"] == "error"
    assert result["code"] == "CTX_001_NO_LAYER"


def test_dashboard_controller_transitions_to_success() -> None:
    controller = DashboardController(session_state={})

    result = controller.on_generate(
        context={"context_version": "ctx-123", "summary_stats": {"count": 3}},
        template_id="distribution",
        params={"field": "population"},
    )

    assert result["state"] == "success"
    assert controller.state == "success"


def test_agent_controller_cancel_returns_timeout_error_state() -> None:
    controller = AgentController(session_state={})
    controller.request_cancel()

    result = controller.on_ask(
        "show me insights",
        context={"context_version": "ctx-123", "summary_stats": {"count": 3}},
    )

    assert result["state"] == "error"
    assert result["code"] == "AI_408_TIMEOUT"
