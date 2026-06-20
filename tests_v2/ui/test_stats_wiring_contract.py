"""Contract checks for plugin wiring to v2 agent controls."""

from pathlib import Path


def _stats_source() -> str:
    stats_path = Path(__file__).resolve().parents[2] / "Stats.py"
    return stats_path.read_text(encoding="utf-8")


def test_stats_wires_api_key_setup_and_ask_buttons() -> None:
    source = _stats_source()

    assert "apiKeySetupButton.clicked.connect" in source
    assert "askAgentButton.clicked.connect" in source


def test_stats_applies_ai_401_gate_to_ask_button() -> None:
    source = _stats_source()

    assert "self.dlg.askAgentButton.setEnabled(is_valid)" in source
    assert "AI_401_KEY_INVALID" in source


def test_stats_uses_v2_agent_controller() -> None:
    source = _stats_source()

    assert "AgentController" in source
