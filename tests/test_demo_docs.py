"""Tests for the SignalForge-to-AlphaForge demo runbook."""

import importlib.util
import re
import subprocess
from pathlib import Path
from types import ModuleType


def load_demo_script() -> ModuleType:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "run_signalforge_alphaforge_demo.py"
    spec = importlib.util.spec_from_file_location("run_signalforge_alphaforge_demo", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_git(args: list[str], *, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, text=True, capture_output=True)


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
        "Summary Metadata",
        "signalforge_repo",
        "signalforge_head",
        "signalforge_dirty",
        "alphaforge_repo",
        "alphaforge_head",
        "alphaforge_dirty",
        "SignalForge does not run backtests",
        "AlphaForge does not compute SignalForge factors",
        "AlphaForge does not import SignalForge runtime",
        "signal_value is ignored for execution",
        "Known Limitations",
    ]
    for term in required_terms:
        assert term in content


def test_signalforge_alphaforge_checkpoint_doc_exists_with_required_terms() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    checkpoint_path = (
        repo_root
        / "docs"
        / "releases"
        / "signalforge-alphaforge-e2e-checkpoint.md"
    )

    assert checkpoint_path.exists()

    content = checkpoint_path.read_text(encoding="utf-8")
    required_terms = [
        "FIRST E2E DEMO PASSED",
        "SignalForge",
        "AlphaForge",
        "signal.csv",
        "custom_signal",
        "commit metadata",
        "no SignalForge runtime import",
        "ruff check",
    ]
    for term in required_terms:
        assert term in content


def test_demo_git_metadata_helper_reads_head_and_dirty_status(tmp_path: Path) -> None:
    demo_script = load_demo_script()
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    run_git(["init"], cwd=repo_path)
    run_git(["config", "user.name", "SignalForge Test"], cwd=repo_path)
    run_git(["config", "user.email", "signalforge-test@example.com"], cwd=repo_path)
    tracked_file = repo_path / "tracked.txt"
    tracked_file.write_text("initial\n", encoding="utf-8")
    run_git(["add", "tracked.txt"], cwd=repo_path)
    run_git(["commit", "-m", "initial"], cwd=repo_path)

    metadata = demo_script.read_git_metadata(repo_path)

    assert metadata["repo"] == str(repo_path.resolve())
    assert re.fullmatch(r"[0-9a-f]{40}", metadata["head"])
    assert metadata["dirty"] is False

    tracked_file.write_text("changed\n", encoding="utf-8")

    dirty_metadata = demo_script.read_git_metadata(repo_path)

    assert dirty_metadata["head"] == metadata["head"]
    assert dirty_metadata["dirty"] is True


def test_require_clean_repos_rejects_dirty_metadata() -> None:
    demo_script = load_demo_script()

    try:
        demo_script.require_clean_repos({"repo": "/clean", "dirty": False}, {"repo": "/dirty", "dirty": True})
    except SystemExit as exc:
        assert "--require-clean-repos" in str(exc)
        assert "/dirty" in str(exc)
    else:
        raise AssertionError("Expected dirty metadata to fail clean-repository enforcement")
