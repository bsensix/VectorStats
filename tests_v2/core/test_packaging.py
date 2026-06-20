"""Tests for packaging and release artifacts."""

from pathlib import Path
import subprocess
import sys


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_v2_package_paths_listed_in_pb_tool() -> None:
    content = (_repo_root() / "pb_tool.cfg").read_text(encoding="utf-8")
    assert "vectorstats_v2" in content


def test_makefile_extra_dirs_include_vectorstats_v2() -> None:
    content = (_repo_root() / "Makefile").read_text(encoding="utf-8")
    assert "EXTRA_DIRS = vectorstats_v2" in content


def test_openai_setup_doc_exists() -> None:
    doc_path = _repo_root() / "docs" / "v2" / "openai-setup.md"
    assert doc_path.exists()


def test_benchmark_script_supports_dry_run() -> None:
    script_path = _repo_root() / "scripts" / "benchmark_time_to_insight.py"
    completed = subprocess.run(
        [sys.executable, str(script_path), "--dry-run"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "dry-run" in completed.stdout.lower()
