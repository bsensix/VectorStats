"""UI contract tests for required v2 tab labels."""

from pathlib import Path
import xml.etree.ElementTree as ET


def _ui_root() -> ET.Element:
    ui_path = Path(__file__).resolve().parents[2] / "Stats_dialog_base.ui"
    tree = ET.parse(ui_path)
    return tree.getroot()


def test_dialog_has_dashboard_and_agent_tabs() -> None:
    root = _ui_root()

    titles = [node.text for node in root.findall(".//widget/widget/attribute/string")]
    assert "Dashboard" in titles
    assert "Agent" in titles


def test_dialog_has_key_setup_and_agent_controls() -> None:
    root = _ui_root()

    button_names = [
        node.attrib.get("name")
        for node in root.findall(".//widget[@class='QPushButton']")
    ]
    assert "apiKeySetupButton" in button_names
    assert "askAgentButton" in button_names
