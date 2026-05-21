"""Run the real SignalForge-to-AlphaForge end-to-end demo."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

import pandas as pd
import yaml


SIGNAL_NAME = "moskowitz_momentum"
SOURCE = "signalforge_e2e_demo"
SYMBOL = "SFDEMO"
START_DATE = "2024-01-02"
END_DATE = "2025-03-31"
DEVELOPMENT_START = "2024-01-02"
DEVELOPMENT_END = "2025-01-31"
HOLDOUT_START = "2025-02-03"
HOLDOUT_END = "2025-03-31"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the SignalForge-to-AlphaForge E2E demo")
    parser.add_argument(
        "--alphaforge-repo",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "AlphaForge",
        help="Path to the sibling AlphaForge repository.",
    )
    parser.add_argument(
        "--work-dir",
        type=Path,
        default=Path("artifacts") / "signalforge_to_alphaforge_e2e",
        help="Demo working directory. Defaults under ignored artifacts/.",
    )
    parser.add_argument("--keep-existing", action="store_true", help="Do not clear the demo working directory first.")
    args = parser.parse_args()

    signalforge_repo = Path(__file__).resolve().parents[1]
    alphaforge_repo = args.alphaforge_repo.resolve()
    work_dir = (signalforge_repo / args.work_dir).resolve()

    if not alphaforge_repo.exists():
        raise SystemExit(f"AlphaForge repository not found: {alphaforge_repo}")
    if not args.keep_existing and work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    input_dir = work_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    market_data_path = input_dir / "market_data.csv"
    config_path = input_dir / "signalforge_config.yaml"

    market_data = build_demo_market_data()
    market_data.to_csv(market_data_path, index=False)
    write_signalforge_config(config_path, market_data_path, work_dir / "signalforge")

    signalforge_command = [
        sys.executable,
        "-m",
        "signalforge.cli",
        "--config",
        str(config_path),
        "--overwrite",
    ]
    run_command(signalforge_command, cwd=signalforge_repo, env=pythonpath_env(signalforge_repo / "src"))

    artifact_dir = (
        work_dir
        / "signalforge"
        / SYMBOL
        / SIGNAL_NAME
        / f"{START_DATE.replace('-', '')}_{END_DATE.replace('-', '')}"
    )
    signal_csv = artifact_dir / "signal.csv"
    signal_contract = artifact_dir / "signal_contract.yaml"
    data_quality_report = artifact_dir / "data_quality_report.json"
    require_files(signal_csv, signal_contract, data_quality_report)

    custom_signal_checks = run_custom_signal_checks(
        alphaforge_repo=alphaforge_repo,
        market_data_path=market_data_path,
        signal_csv=signal_csv,
        work_dir=work_dir,
    )

    alphaforge_output_dir = work_dir / "alphaforge"
    alphaforge_command = [
        sys.executable,
        "-m",
        "alphaforge.cli",
        "research-validate",
        "--strategy",
        "custom_signal",
        "--data",
        str(market_data_path),
        "--symbol",
        SYMBOL,
        "--signal-file",
        str(signal_csv),
        "--signal-name",
        SIGNAL_NAME,
        "--development-start",
        DEVELOPMENT_START,
        "--development-end",
        DEVELOPMENT_END,
        "--holdout-start",
        HOLDOUT_START,
        "--holdout-end",
        HOLDOUT_END,
        "--train-size",
        "80",
        "--test-size",
        "20",
        "--step-size",
        "20",
        "--initial-capital",
        "1000",
        "--fee-rate",
        "0",
        "--slippage-rate",
        "0",
        "--annualization-factor",
        "252",
        "--output-dir",
        str(alphaforge_output_dir),
        "--experiment-name",
        "signalforge_to_alphaforge_e2e",
    ]
    alphaforge_result = run_command(
        alphaforge_command,
        cwd=alphaforge_repo,
        env=pythonpath_env(alphaforge_repo / "src"),
    )
    alphaforge_payload = json.loads(alphaforge_result.stdout)

    generated_alphaforge_artifacts = sorted(
        str(path)
        for path in (alphaforge_output_dir / "signalforge_to_alphaforge_e2e").rglob("*")
        if path.is_file()
    )
    if not generated_alphaforge_artifacts:
        raise SystemExit("AlphaForge did not generate output artifacts")

    summary = {
        "signalforge_command": signalforge_command,
        "alphaforge_command": alphaforge_command,
        "generated_signalforge_artifacts": [
            str(signal_csv),
            str(signal_contract),
            str(data_quality_report),
        ],
        "generated_alphaforge_artifacts": generated_alphaforge_artifacts,
        "custom_signal_checks": custom_signal_checks,
        "alphaforge_summary": {
            "selected_strategy": alphaforge_payload.get("selected_strategy"),
            "selection_rule": alphaforge_payload.get("selection_rule"),
            "research_protocol_summary_path": alphaforge_payload.get("research_protocol_summary_path"),
        },
        "runtime_behavior_changed": False,
        "signalforge_runtime_imported_by_alphaforge": custom_signal_checks["signalforge_runtime_imported"],
    }
    print(json.dumps(summary, indent=2))


def build_demo_market_data() -> pd.DataFrame:
    dates = pd.bdate_range(START_DATE, END_DATE)
    rows: list[dict[str, object]] = []
    previous_close = 100.0
    for idx, date in enumerate(dates):
        close = 100.0 + idx * 0.08 + ((idx % 17) - 8) * 0.03
        open_price = previous_close + ((idx % 5) - 2) * 0.04
        high = max(open_price, close) + 0.65
        low = min(open_price, close) - 0.65
        rows.append(
            {
                "datetime": date.strftime("%Y-%m-%d"),
                "open": round(open_price, 4),
                "high": round(high, 4),
                "low": round(low, 4),
                "close": round(close, 4),
                "volume": 1_000_000 + idx * 1000,
            }
        )
        previous_close = close
    return pd.DataFrame(rows)


def write_signalforge_config(config_path: Path, market_data_path: Path, artifacts_dir: Path) -> None:
    config = {
        "signal_name": SIGNAL_NAME,
        "source": SOURCE,
        "factor_name": SIGNAL_NAME,
        "factor_params": {
            "lookback_days": 252,
            "skip_days": 21,
        },
        "data_source": {
            "type": "local_ohlcv_csv",
            "path": str(market_data_path),
            "symbol": SYMBOL,
        },
        "datetime_range": {
            "start": f"{START_DATE}T00:00:00Z",
            "end": f"{END_DATE}T23:59:59Z",
        },
        "output": {
            "artifacts_dir": str(artifacts_dir),
        },
    }
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")


def run_custom_signal_checks(
    *,
    alphaforge_repo: Path,
    market_data_path: Path,
    signal_csv: Path,
    work_dir: Path,
) -> dict[str, object]:
    checks_path = work_dir / "custom_signal_checks.json"
    check_script = dedent(
        f"""
        import builtins
        import json
        import sys
        from pathlib import Path

        import pandas as pd

        original_import = builtins.__import__
        imported_signalforge_names = []

        def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name.lower().startswith("signalforge"):
                imported_signalforge_names.append(name)
                raise AssertionError(f"AlphaForge must not import SignalForge runtime module {{name!r}}")
            return original_import(name, globals, locals, fromlist, level)

        builtins.__import__ = guarded_import

        from alphaforge.custom_signal import load_custom_signal_positions
        from alphaforge.data_loader import load_market_data
        from alphaforge.schemas import DataSpec

        market_data = load_market_data(DataSpec(path=Path({str(market_data_path)!r}), symbol={SYMBOL!r}))
        target_position, metadata = load_custom_signal_positions(
            Path({str(signal_csv)!r}),
            market_data,
            symbol={SYMBOL!r},
            signal_name={SIGNAL_NAME!r},
        )

        signal_frame = pd.read_csv(Path({str(signal_csv)!r}))
        raw_signal_frame = signal_frame.copy()
        signal_frame["datetime"] = pd.to_datetime(signal_frame["datetime"], utc=False)
        market_datetimes = pd.to_datetime(market_data["datetime"], utc=False)
        mapped = signal_frame.set_index("datetime")["signal_binary"].astype(float)
        expected = mapped.reindex(market_datetimes, fill_value=0.0).tolist()

        extra_signal = raw_signal_frame.copy()
        extra_row = extra_signal.iloc[-1].copy()
        extra_row["datetime"] = "2030-01-02"
        extra_row["available_at"] = "2030-01-02"
        extra_signal = pd.concat([extra_signal, extra_row.to_frame().T], ignore_index=True)
        extra_path = Path({str(work_dir / "extra_signal_date.csv")!r})
        extra_signal.to_csv(extra_path, index=False)

        extra_date_failed = False
        try:
            load_custom_signal_positions(extra_path, market_data, symbol={SYMBOL!r}, signal_name={SIGNAL_NAME!r})
        except ValueError as exc:
            extra_date_failed = "signal dates must align with market data dates" in str(exc)

        result = {{
            "schema_validation_passed": True,
            "signal_binary_maps_to_target_position": target_position.tolist() == expected,
            "missing_signal_dates_default_flat": all(
                value == 0.0
                for date, value in zip(market_datetimes, target_position.tolist(), strict=True)
                if date not in set(mapped.index)
            ),
            "extra_signal_dates_fail": extra_date_failed,
            "signalforge_runtime_imported": bool(imported_signalforge_names)
                or any(name.lower().startswith("signalforge") for name in sys.modules),
            "metadata": metadata,
        }}
        Path({str(checks_path)!r}).write_text(json.dumps(result, indent=2), encoding="utf-8")
        """
    )
    run_command(
        [sys.executable, "-c", check_script],
        cwd=alphaforge_repo,
        env=pythonpath_env(alphaforge_repo / "src"),
    )
    checks = json.loads(checks_path.read_text(encoding="utf-8"))
    failed = [name for name, passed in checks.items() if name != "metadata" and passed is not True and passed is not False]
    if failed:
        raise SystemExit(f"Unexpected custom-signal check payload values: {failed}")
    required_true = [
        "schema_validation_passed",
        "signal_binary_maps_to_target_position",
        "missing_signal_dates_default_flat",
        "extra_signal_dates_fail",
    ]
    missing = [name for name in required_true if checks.get(name) is not True]
    if missing:
        raise SystemExit(f"Custom-signal checks failed: {missing}")
    if checks.get("signalforge_runtime_imported") is not False:
        raise SystemExit("AlphaForge imported SignalForge runtime during demo checks")
    return checks


def run_command(command: list[str], *, cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise SystemExit(
            "Command failed:\n"
            f"cwd: {cwd}\n"
            f"command: {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result


def pythonpath_env(path: Path) -> dict[str, str]:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(path) if not existing else os.pathsep.join([str(path), existing])
    return env


def require_files(*paths: Path) -> None:
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise SystemExit(f"Missing expected generated files: {missing}")


if __name__ == "__main__":
    main()
