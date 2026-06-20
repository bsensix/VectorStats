"""Tests for API key validation gate in Agent controller."""

from vectorstats_v2.ui.agent_controller import AgentController


def test_ask_action_starts_disabled_without_valid_key() -> None:
    controller = AgentController(session_state={})

    assert controller.ask_enabled is False


def test_invalid_key_keeps_gate_closed_and_sets_ai_401_error() -> None:
    controller = AgentController(session_state={})

    valid = controller.validate_api_key("invalid")

    assert valid is False
    assert controller.ask_enabled is False
    assert controller.last_error_code == "AI_401_KEY_INVALID"


def test_valid_key_opens_gate_for_agent_requests() -> None:
    controller = AgentController(session_state={})

    valid = controller.validate_api_key("sk-test-key-123456")

    assert valid is True
    assert controller.ask_enabled is True
    assert controller.last_error_code is None
