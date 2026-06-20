"""Tests for context version continuity between Dashboard and Agent tabs."""

from vectorstats_v2.core.session_state import SessionState
from vectorstats_v2.ui.agent_controller import AgentController
from vectorstats_v2.ui.dashboard_controller import DashboardController


def test_dashboard_and_agent_share_same_context_version() -> None:
    session_state = SessionState()
    dashboard = DashboardController(session_state=session_state)
    agent = AgentController(session_state=session_state)

    dashboard_result = dashboard.on_generate(
        context={"context_version": "ctx-shared", "summary_stats": {"count": 10}},
        template_id="distribution",
        params={"field": "population"},
    )
    dashboard_version = dashboard_result["context_version"]
    agent.validate_api_key("sk-test-key-123456")

    agent_result = agent.on_ask(
        "analyze this",
        context={"context_version": "ctx-shared", "summary_stats": {"count": 10}},
    )
    agent_version = agent_result["context_version"]

    assert dashboard_version == agent_version
    assert session_state.get("active_context_version") == "ctx-shared"
