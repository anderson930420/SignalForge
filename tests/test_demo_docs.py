"""Tests for the SignalForge-to-AlphaForge demo runbook."""

from pathlib import Path


def test_signalforge_to_alphaforge_demo_doc_exists_with_required_sections() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    doc_path = repo_root / "docs" / "demos" / "signalforge_to_alphaforge_e2e.md"
    script_path = repo_root / "scripts" / "run_signalforge_alphaforge_demo.py"

    assert doc_path.exists()
    assert script_path.exists()

    content = doc_path.read_text(encoding="utf-8")
    required_terms = [
        "Purpose",
        "Prerequisites",
        "SignalForge Command",
        "AlphaForge Command",
        "Generated SignalForge Artifacts",
        "Generated AlphaForge Artifacts",
        "Validation Results",
        "SignalForge does not run backtests",
        "AlphaForge does not compute SignalForge factors",
        "AlphaForge does not import SignalForge runtime",
        "signal_value is ignored for execution",
        "Known Limitations",
    ]
    for term in required_terms:
        assert term in content
