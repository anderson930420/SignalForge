"""Tests for README and documentation."""

from pathlib import Path


def test_readme_contains_key_sections():
    readme_path = Path(__file__).parent.parent / "README.md"
    assert readme_path.exists(), "README.md must exist"

    content = readme_path.read_text()

    assert "not a backtester" in content, "README must state SignalForge is not a backtester"
    assert "signal.csv" in content, "README must document signal.csv"
    assert "signal_contract.yaml" in content, "README must document signal_contract.yaml"
    assert "data_quality_report.json" in content, "README must document data_quality_report.json"
    assert "AlphaForge" in content, "README must mention AlphaForge"

    assert "Moskowitz" in content, "README must document Moskowitz factor"
    assert "lookback_days" in content, "README must document Moskowitz parameters"

    assert "datetime" in content and "available_at" in content and "signal_binary" in content, \
        "README must document signal.csv columns"
    assert "daily trading-date label" in content, \
        "README must document daily trading-date label semantics"
    assert "Offset timestamps should be treated by declared trading date" in content or \
        "not by UTC-shifted instant time" in content, \
        "README must document offset timestamp daily alignment"

    assert "python -m pytest" in content, "README must document pytest command"
    assert "ruff check" in content, "README must document ruff check"
    assert "openspec validate" in content, "README must document openspec validate"

    assert "docs/alphaforge_handoff.md" in content, \
        "README must link to docs/alphaforge_handoff.md"


def test_handoff_doc_contains_key_sections():
    handoff_path = Path(__file__).parent.parent / "docs" / "alphaforge_handoff.md"
    assert handoff_path.exists(), "docs/alphaforge_handoff.md must exist"

    content = handoff_path.read_text()

    assert "AlphaForge" in content, "handoff doc must mention AlphaForge"
    assert "signal.csv" in content, "handoff doc must document signal.csv"
    assert "custom_signal" in content, "handoff doc must document custom_signal interface"
    assert "not run backtests" in content or "does not run backtests" in content, \
        "handoff doc must state SignalForge does not run backtests"
    assert "available_at <=" in content, \
        "handoff doc must document available_at <= datetime rule"
    assert "Daily datetime policy" in content, \
        "handoff doc must document daily datetime policy"
    assert "should not UTC-shift the declared date" in content, \
        "handoff doc must document no UTC-shift daily alignment"
