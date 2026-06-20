"""Tests for narrative formatting and schema safeguards."""

from vectorstats_v2.core.insight_formatter import format_narrative


def test_insight_formatter_reports_ins_001_when_section_missing() -> None:
    result = format_narrative("Diagnostic: ok")

    assert result.error_code in {
        None,
        "INS_001_MISSING_SECTION",
        "INS_002_PARSE_FAILURE",
    }


def test_insight_formatter_extracts_all_required_sections() -> None:
    response = (
        "Diagnostic: Stable trend\n"
        "Key findings: Demand grew 12%\n"
        "Risks: Outliers in zone B\n"
        "Recommended actions: Review zone B records"
    )
    result = format_narrative(response)

    assert result.error_code is None
    assert result.blocks["diagnostic"]
    assert result.blocks["key_findings"]
    assert result.blocks["risks"]
    assert result.blocks["recommended_actions"]
