"""Release gate tests for narrative schema quality."""

from pathlib import Path
import subprocess
import sys

from vectorstats_v2.core.insight_formatter import evaluate_schema_pass_rate


def test_narrative_schema_pass_rate_is_at_least_99_percent() -> None:
    sample_runs = [
        True,
        True,
        True,
        True,
        True,
        True,
        True,
        True,
        True,
        True,
    ]
    pass_rate = evaluate_schema_pass_rate(sample_runs)
    assert pass_rate >= 0.99


def test_narrative_schema_gate_detects_regression() -> None:
    sample_runs = [True, False, True, False, True]
    pass_rate = evaluate_schema_pass_rate(sample_runs)
    assert pass_rate < 0.99


def test_benchmark_dry_run_mentions_schema_gate() -> None:
    script = (
        Path(__file__).resolve().parents[2] / "scripts" / "benchmark_time_to_insight.py"
    )
    completed = subprocess.run(
        [sys.executable, str(script), "--dry-run"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "schema gate" in completed.stdout.lower()
