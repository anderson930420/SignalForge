from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest
import yaml

from scripts.download_tw_ohlcv import normalize_yfinance_ohlcv_frame
from scripts.run_tw_multi_symbol_pipeline import (
    build_signal_name,
    parse_symbols,
    run_tw_multi_symbol_pipeline,
    symbol_slug,
)


def _fake_downloader(symbol, start, end, auto_adjust=False, progress=False):
    return pd.DataFrame(
        {
            "Open": [100.0, 101.0, 102.0],
            "High": [101.0, 102.0, 103.0],
            "Low": [99.0, 100.0, 101.0],
            "Close": [100.5, 101.5, 102.5],
            "Volume": [1000, 1100, 1200],
        },
        index=pd.to_datetime(["2021-01-04", "2021-01-05", "2021-01-06"]),
    ).rename_axis("Date")


def test_normalize_yfinance_ohlcv_frame_handles_date_index() -> None:
    raw = _fake_downloader("2330.TW", "2021-01-01", "2021-01-10")
    normalized = normalize_yfinance_ohlcv_frame(raw)

    assert normalized.columns.tolist() == ["datetime", "open", "high", "low", "close", "volume"]
    assert normalized["open"].tolist() == [100.0, 101.0, 102.0]


def test_parse_symbols_dedupes_and_reads_file(tmp_path: Path) -> None:
    symbols_file = tmp_path / "symbols.txt"
    symbols_file.write_text("# comment\n0050.TW\n2330.TW\n", encoding="utf-8")

    assert parse_symbols("2330.TW,2317.TW", symbols_file) == ["2330.TW", "2317.TW", "0050.TW"]


def test_parse_symbols_requires_input() -> None:
    with pytest.raises(ValueError, match="At least one symbol"):
        parse_symbols(None, None)


def test_symbol_naming_helpers_are_stable() -> None:
    assert symbol_slug("2330.TW") == "2330_tw"
    assert build_signal_name("2330.TW") == "tw_2330_tw_moskowitz_v02"


def test_run_tw_multi_symbol_pipeline_builds_configs_and_commands(tmp_path: Path) -> None:
    output_root = tmp_path / "tw_multi_symbol"
    calls: list[tuple[list[str], Path | None]] = []

    def fake_runner(command, *, cwd=None, text=True, capture_output=True, check=False):
        calls.append((list(command), cwd))
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    summary = run_tw_multi_symbol_pipeline(
        symbols=["2330.TW", "0050.TW"],
        start="2021-01-01",
        end="2022-01-01",
        output_root=output_root,
        overwrite=True,
        runner=fake_runner,
        downloader=_fake_downloader,
        repo_root=tmp_path,
    )

    assert summary["status"] == "completed"
    assert summary["symbol_count"] == 2
    assert Path(summary["summary_path"]).exists()

    for symbol in ["2330.TW", "0050.TW"]:
        slug = symbol.lower().replace(".", "_")
        data_csv = output_root / "data" / f"{slug}_ohlcv.csv"
        config_yaml = output_root / "configs" / f"{slug}_moskowitz_v02.yaml"

        assert data_csv.exists()
        assert config_yaml.exists()

        config = yaml.safe_load(config_yaml.read_text(encoding="utf-8"))
        assert config["signal_contract_version"] == "v0.2"
        assert config["data_source"]["symbol"] == symbol
        assert config["factor_name"] == "moskowitz_momentum"
        assert config["target_weight"]["method"] == "signed_unit"

    assert len(calls) == 4
    assert calls[0][0][:4] == [sys.executable, "-m", "signalforge.cli", "generate"]
    assert calls[1][0][:4] == [sys.executable, "-m", "signalforge.cli", "package-alphaforge-v02"]
    assert calls[2][0][:4] == [sys.executable, "-m", "signalforge.cli", "generate"]
    assert calls[3][0][:4] == [sys.executable, "-m", "signalforge.cli", "package-alphaforge-v02"]

    package_commands = [call[0] for call in calls if "package-alphaforge-v02" in call[0]]
    assert all("--overwrite" in command for command in package_commands)

    saved_summary = json.loads((output_root / "tw_multi_symbol_summary.json").read_text(encoding="utf-8"))
    assert saved_summary["symbol_count"] == 2


def test_run_tw_multi_symbol_pipeline_refuses_existing_outputs_without_overwrite(tmp_path: Path) -> None:
    output_root = tmp_path / "tw_multi_symbol"
    existing = output_root / "data" / "2330_tw_ohlcv.csv"
    existing.parent.mkdir(parents=True)
    existing.write_text("already here\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="Data file already exists"):
        run_tw_multi_symbol_pipeline(
            symbols=["2330.TW"],
            start="2021-01-01",
            end="2022-01-01",
            output_root=output_root,
            overwrite=False,
            runner=lambda *args, **kwargs: subprocess.CompletedProcess(args, 0, stdout="ok", stderr=""),
            downloader=_fake_downloader,
            repo_root=tmp_path,
        )
