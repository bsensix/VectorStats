"""Tests for persisting and restoring session configuration."""

from vectorstats_v2.core.session_state import SessionState
from vectorstats_v2.ui.agent_controller import AgentController
from vectorstats_v2.ui.dashboard_controller import DashboardController


def test_session_restore_reapplies_last_layer_filters_template_and_queries(
    tmp_path,
) -> None:
    state_file = tmp_path / "session_state.json"
    session = SessionState(path=state_file)

    payload = {
        "layer_id": "layer-1",
        "filters": {"min": 10},
        "template_id": "distribution",
        "recent_queries": ["q1"],
    }
    session.save(payload)

    restored = session.load()
    assert restored["layer_id"] == "layer-1"
    assert restored["template_id"] == "distribution"


def test_controllers_apply_saved_state() -> None:
    dashboard = DashboardController(session_state={})
    agent = AgentController(session_state={})

    saved = {
        "layer_id": "layer-1",
        "filters": {"city": "Recife"},
        "template_id": "distribution",
        "recent_queries": ["show trends"],
    }

    dashboard.apply_saved_state(saved)
    agent.apply_saved_state(saved)

    assert dashboard.last_layer_id == "layer-1"
    assert dashboard.last_template_id == "distribution"
    assert agent.recent_queries == ["show trends"]
