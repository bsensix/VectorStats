"""Lightweight E2E flow from dashboard generation to agent insight."""

from vectorstats_v2.ui.agent_controller import AgentController
from vectorstats_v2.ui.dashboard_controller import DashboardController


class FakeAgentClient:
    def generate(self, context: dict[str, object], prompt: str) -> str:
        _ = context
        _ = prompt
        return (
            "Diagnostic: Stable distribution\n"
            "Key findings: Segment A has highest concentration\n"
            "Risks: Outliers in segment C\n"
            "Recommended actions: Review segment C data quality"
        )


def test_layer_to_dashboard_to_agent_flow() -> None:
    session_state: dict[str, object] = {}
    dashboard = DashboardController(session_state=session_state)
    agent = AgentController(session_state=session_state, agent_client=FakeAgentClient())

    dashboard_result = dashboard.on_generate(
        context={
            "context_version": "ctx-e2e",
            "summary_stats": {"count": 15, "mean": 42.0},
        },
        template_id="distribution",
        params={"field": "population"},
    )

    assert dashboard_result["state"] == "success"
    assert dashboard_result["context_version"] == "ctx-e2e"

    assert agent.validate_api_key("sk-e2e-test-key") is True
    agent_result = agent.on_ask(
        "generate insight",
        context={
            "context_version": "ctx-e2e",
            "summary_stats": {"count": 15, "mean": 42.0},
        },
    )

    assert agent_result["state"] == "success"
    narrative = agent_result["narrative"]
    assert "diagnostic" in narrative
    assert "key_findings" in narrative
    assert "risks" in narrative
    assert "recommended_actions" in narrative
