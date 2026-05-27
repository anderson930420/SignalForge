#!/usr/bin/env python3
"""Run a multi-symbol Taiwan OHLCV -> SignalForge -> AlphaForge-package pipeline.

This script orchestrates existing SignalForge CLI boundaries. It does not add a
new signal schema and does not run AlphaForge.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.download_tw_ohlcv import download_tw_ohlcv


@dataclass(frozen=True)
class SymbolPipelineResult:
    symbol: str
    data_csv: Path
    config_yaml: Path
    artifact_dir: Path
    package_dir: Path


class CommandRunner(Protocol):
    def __call__(
        self,
        command: Sequence[str],
        *,
        cwd: Path | None = None,
        text: bool = True,
        capture_output: bool = True,
        check: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        ...


def parse_symbols(raw_symbols: str | None, symbols_file: Path | None = None) -> list[str]:
    symbols: list[str] = []

    if raw_symbols:
        symbols.extend(piece.strip() for piece in raw_symbols.split(",") if piece.strip())

    if symbols_file is not None:
        for line in symbols_file.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                symbols.append(stripped)

    deduped: list[str] = []
    seen: set[str] = set()
    for symbol in symbols:
        if symbol not in seen:
            deduped.append(symbol)
            seen.add(symbol)

    if not deduped:
        raise ValueError("At least one symbol is required via --symbols or --symbols-file")

    return deduped


def symbol_slug(symbol: str) -> str:
    return symbol.lower().replace(".", "_").replace("-", "_")


def date_slug(date_value: str) -> str:
    return date_value[:10].replace("-", "")


def build_signal_name(symbol: str) -> str:
    return f"tw_{symbol_slug(symbol)}_moskowitz_v02"


def build_config(
    *,
    symbol: str,
    data_csv: Path,
    output_root: Path,
    start: str,
    end: str,
) -> dict:
    return {
        "signal_name": build_signal_name(symbol),
        "source": f"yfinance_{symbol_slug(symbol)}",
        "factor_name": "moskowitz_momentum",
        "signal_contract_version": "v0.2",
        "target_weight": {
            "method": "signed_unit",
            "max_abs_weight": 1.0,
            "neutral_threshold": 0.0,
        },
        "data_source": {
            "type": "local_ohlcv_csv",
            "path": str(data_csv),
            "symbol": symbol,
        },
        "datetime_range": {
            "start": f"{start[:10]}T00:00:00Z",
            "end": f"{end[:10]}T00:00:00Z",
        },
        "output": {
            "artifacts_dir": str(output_root / "artifacts"),
        },
    }


def write_config(path: Path, config: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return path


def expected_artifact_dir(*, output_root: Path, symbol: str, start: str, end: str) -> Path:
    return (
        output_root
        / "artifacts"
        / symbol
        / build_signal_name(symbol)
        / f"{date_slug(start)}_{date_slug(end)}"
    )


def run_tw_multi_symbol_pipeline(
    *,
    symbols: list[str],
    start: str,
    end: str,
    output_root: Path,
    overwrite: bool = False,
    runner: CommandRunner = subprocess.run,
    downloader=None,
    repo_root: Path | None = None,
) -> dict:
    repo_root = (repo_root or Path.cwd()).resolve()
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    results: list[SymbolPipelineResult] = []

    for symbol in symbols:
        slug = symbol_slug(symbol)
        data_csv = output_root / "data" / f"{slug}_ohlcv.csv"
        config_yaml = output_root / "configs" / f"{slug}_moskowitz_v02.yaml"
        package_dir = output_root / "packages" / symbol
        artifact_dir = expected_artifact_dir(
            output_root=output_root,
            symbol=symbol,
            start=start,
            end=end,
        )

        if data_csv.exists() and not overwrite:
            raise RuntimeError(f"Data file already exists. Use --overwrite: {data_csv}")
        if package_dir.exists() and any(package_dir.iterdir()) and not overwrite:
            raise RuntimeError(f"Package dir already exists. Use --overwrite: {package_dir}")

        download_tw_ohlcv(
            symbol=symbol,
            start=start,
            end=end,
            output=data_csv,
            downloader=downloader,
        )
        write_config(
            config_yaml,
            build_config(
                symbol=symbol,
                data_csv=data_csv,
                output_root=output_root,
                start=start,
                end=end,
            ),
        )

        generate_command = [
            sys.executable,
            "-m",
            "signalforge.cli",
            "generate",
            "--config",
            str(config_yaml),
        ]
        if overwrite:
            generate_command.append("--overwrite")
        _run_checked(runner, generate_command, cwd=repo_root)

        package_command = [
            sys.executable,
            "-m",
            "signalforge.cli",
            "package-alphaforge-v02",
            "--artifact-dir",
            str(artifact_dir),
            "--market-data",
            str(data_csv),
            "--output-dir",
            str(package_dir),
        ]
        if overwrite:
            package_command.append("--overwrite")
        _run_checked(runner, package_command, cwd=repo_root)

        results.append(
            SymbolPipelineResult(
                symbol=symbol,
                data_csv=data_csv,
                config_yaml=config_yaml,
                artifact_dir=artifact_dir,
                package_dir=package_dir,
            )
        )

    summary = {
        "status": "completed",
        "symbol_count": len(results),
        "symbols": [
            {
                "symbol": result.symbol,
                "data_csv": str(result.data_csv),
                "config_yaml": str(result.config_yaml),
                "artifact_dir": str(result.artifact_dir),
                "package_dir": str(result.package_dir),
            }
            for result in results
        ],
    }

    summary_path = output_root / "tw_multi_symbol_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    summary["summary_path"] = str(summary_path)
    return summary


def _run_checked(
    runner: CommandRunner,
    command: Sequence[str],
    *,
    cwd: Path,
) -> subprocess.CompletedProcess[str]:
    result = runner(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "Command failed\n"
            f"cwd: {cwd}\n"
            f"command: {' '.join(command)}\n"
            f"exit_code: {result.returncode}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Taiwan multi-symbol SignalForge pipeline")
    parser.add_argument("--symbols", default=None, help="Comma-separated symbols, e.g. 2330.TW,0050.TW")
    parser.add_argument("--symbols-file", type=Path, default=None, help="Optional newline-delimited symbol file")
    parser.add_argument("--start", required=True, help="Start date, e.g. 2020-01-01")
    parser.add_argument("--end", required=True, help="End date, e.g. 2025-01-01")
    parser.add_argument("--output-root", type=Path, required=True, help="Output root directory")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing outputs")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    symbols = parse_symbols(args.symbols, args.symbols_file)
    summary = run_tw_multi_symbol_pipeline(
        symbols=symbols,
        start=args.start,
        end=args.end,
        output_root=args.output_root,
        overwrite=args.overwrite,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
