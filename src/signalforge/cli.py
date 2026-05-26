"""CLI for SignalForge signal generation."""

import json
from pathlib import Path

import typer

from signalforge.data_registry import local_ohlcv_csv
from signalforge.factor_registry import FactorRegistry
from signalforge.factors.moskowitz_momentum import MoskowitzMomentumFactor
from signalforge.schemas import (
    MissingColumnsError,
    SignalValidationError,
)
from signalforge.signal_composer import SIGNAL_CONTRACT_V01, SignalComposer
from signalforge.signal_semantics import (
    SIGNAL_CONTRACT_V02,
    V02_SIGNAL_COLUMNS,
    SignedUnitWeightPolicy,
    validate_v02_signal_frame,
)
from signalforge.export import (
    export_signal_csv,
    export_signal_contract_yaml,
    export_data_quality_report,
    build_signal_contract,
    build_market_data_quality_report,
)
from signalforge.alphaforge_v02_smoke import export_demo_alphaforge_v02_compatibility_package
from signalforge.compatibility import validate_signal_market_date_alignment


app = typer.Typer(help="SignalForge - Paper-derived factor and standardized signal generation layer")
SUPPORTED_GENERATE_SIGNAL_CONTRACT_VERSIONS = (SIGNAL_CONTRACT_V01, SIGNAL_CONTRACT_V02)


class PipelineError(Exception):
    pass


def validate_config(config: dict) -> list[str]:
    """Validate config and return list of errors."""
    errors = []
    required_fields = [
        "signal_name",
        "source",
        "factor_name",
        "data_source",
        "datetime_range",
        "output",
    ]
    for field in required_fields:
        if field not in config or config[field] is None:
            errors.append(f"Missing required field: {field}")

    signal_contract_version = config.get("signal_contract_version", SIGNAL_CONTRACT_V01)
    if signal_contract_version not in SUPPORTED_GENERATE_SIGNAL_CONTRACT_VERSIONS:
        errors.append(
            "signal_contract_version must be one of "
            f"{list(SUPPORTED_GENERATE_SIGNAL_CONTRACT_VERSIONS)}"
        )

    target_weight_config = config.get("target_weight", {})
    if target_weight_config is not None and not isinstance(target_weight_config, dict):
        errors.append("target_weight must be a dictionary")
    elif signal_contract_version == SIGNAL_CONTRACT_V02 and target_weight_config:
        method = target_weight_config.get("method", "signed_unit")
        if method != "signed_unit":
            errors.append("target_weight.method must be 'signed_unit' for v0.2")
        for target_weight_field in ("max_abs_weight", "neutral_threshold"):
            if target_weight_field in target_weight_config:
                try:
                    float(target_weight_config[target_weight_field])
                except (TypeError, ValueError):
                    errors.append(f"target_weight.{target_weight_field} must be numeric")

    if "data_source" in config:
        ds = config["data_source"]
        if not isinstance(ds, dict):
            errors.append("data_source must be a dictionary")
        elif ds.get("type") != "local_ohlcv_csv":
            errors.append("data_source.type must be 'local_ohlcv_csv'")
        elif "path" not in ds:
            errors.append("data_source.path is required")
        elif "symbol" not in ds:
            errors.append("data_source.symbol is required")

    if "datetime_range" in config:
        dr = config["datetime_range"]
        if not isinstance(dr, dict):
            errors.append("datetime_range must be a dictionary")
        elif "start" not in dr:
            errors.append("datetime_range.start is required")
        elif "end" not in dr:
            errors.append("datetime_range.end is required")

    if "output" in config:
        out = config["output"]
        if not isinstance(out, dict):
            errors.append("output must be a dictionary")
        elif "artifacts_dir" not in out:
            errors.append("output.artifacts_dir is required")

    return errors


def build_output_path(
    artifacts_dir: str,
    symbol: str,
    signal_name: str,
    start_date: str,
    end_date: str,
) -> Path:
    """Build deterministic output path."""
    start_clean = start_date.split("T")[0].replace("-", "")
    end_clean = end_date.split("T")[0].replace("-", "")
    return Path(artifacts_dir) / symbol / signal_name / f"{start_clean}_{end_clean}"


def check_files_exist(output_dir: Path) -> list[Path]:
    """Check which required files already exist."""
    files = [
        output_dir / "signal.csv",
        output_dir / "signal_contract.yaml",
        output_dir / "data_quality_report.json",
    ]
    return [f for f in files if f.exists()]


def build_signed_unit_weight_policy(config: dict) -> SignedUnitWeightPolicy:
    """Build a v0.2 signed-unit target-weight policy from config."""
    target_weight_config = config.get("target_weight") or {}
    method = target_weight_config.get("method", "signed_unit")
    if method != "signed_unit":
        raise ValueError("target_weight.method must be 'signed_unit' for v0.2")
    return SignedUnitWeightPolicy(
        max_abs_weight=float(target_weight_config.get("max_abs_weight", 1.0)),
        neutral_threshold=float(target_weight_config.get("neutral_threshold", 0.0)),
    )


def export_generated_signal_csv(
    signal_df,
    output_dir: Path,
    *,
    signal_contract_version: str,
) -> Path:
    """Export generated v0.1 or v0.2 signal.csv rows."""
    if signal_contract_version == SIGNAL_CONTRACT_V01:
        return export_signal_csv(signal_df, output_dir, validate=True)

    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / "signal.csv"
    v02_signal = validate_v02_signal_frame(signal_df)
    v02_signal = v02_signal.sort_values(
        by=["datetime", "symbol", "signal_name"],
        kind="mergesort",
    ).reset_index(drop=True)
    v02_signal.to_csv(filepath, index=False, lineterminator="\n")
    return filepath


def build_v02_signal_contract(
    *,
    signal_name: str,
    source: str,
    factor_name: str,
    parameters: dict,
    timing_rule: str,
    symbols: list[str],
    datetime_range: tuple[str, str],
    factor_version: str,
    target_weight_config: dict,
) -> dict:
    """Build deterministic v0.2 signal contract metadata."""
    return {
        "signal_name": signal_name,
        "version": "0.2.0",
        "source": source,
        "factor": {
            "name": factor_name,
            "version": factor_version,
            "parameters": dict(sorted(parameters.items())) if parameters else {},
        },
        "decision_rule": {
            "score": "factor_value",
            "direction": "sign(score) with optional neutral_threshold",
            "target_weight": "direction * max_abs_weight using signed_unit policy",
        },
        "target_weight": {
            "method": "signed_unit",
            "max_abs_weight": float(target_weight_config.get("max_abs_weight", 1.0)),
            "neutral_threshold": float(target_weight_config.get("neutral_threshold", 0.0)),
        },
        "data": {
            "required_columns": ["datetime", "open", "high", "low", "close", "volume", "symbol"],
        },
        "timing": {
            "available_at_rule": timing_rule,
        },
        "output": {
            "file": "signal.csv",
            "schema_version": SIGNAL_CONTRACT_V02,
            "columns": list(V02_SIGNAL_COLUMNS),
        },
        "compatibility": {
            "alphaforge_custom_signal_version": "v0.2",
            "expected_execution_semantics": "signed_close_to_close_lagged",
        },
        "symbols": symbols,
        "datetime_range": {
            "start": datetime_range[0],
            "end": datetime_range[1],
        },
    }


@app.callback(invoke_without_command=True)
def default_generate_compatibility(
    ctx: typer.Context,
    config: Path | None = typer.Option(None, "--config", "-c", help="Path to YAML config file"),
    overwrite: bool = typer.Option(False, "--overwrite", "-o", help="Overwrite existing output files"),
) -> None:
    """Preserve legacy `signalforge --config ...` invocation after adding subcommands."""
    if ctx.invoked_subcommand is not None:
        return
    if config is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)
    generate(config=config, overwrite=overwrite)


@app.command()
def generate(
    config: Path = typer.Option(..., "--config", "-c", help="Path to YAML config file"),
    overwrite: bool = typer.Option(False, "--overwrite", "-o", help="Overwrite existing output files"),
) -> None:
    """Generate signal artifacts from a YAML config file."""
    import yaml
    from signalforge.schemas import SignalValidator

    if not config.exists():
        typer.echo(f"Error: Config file not found: {config}", err=True)
        raise typer.Exit(1)

    try:
        with open(config) as f:
            cfg = yaml.safe_load(f)
    except yaml.YAMLError as e:
        typer.echo(f"Error: Failed to parse YAML: {e}", err=True)
        raise typer.Exit(1)

    errors = validate_config(cfg)
    if errors:
        for err in errors:
            typer.echo(f"Error: {err}", err=True)
        raise typer.Exit(1)

    signal_name = cfg["signal_name"]
    source = cfg["source"]
    factor_name = cfg["factor_name"]
    data_source = cfg["data_source"]
    datetime_range = cfg["datetime_range"]
    output_config = cfg["output"]
    signal_contract_version = cfg.get("signal_contract_version", SIGNAL_CONTRACT_V01)
    target_weight_config = cfg.get("target_weight") or {}

    data_path = data_source["path"]
    symbol = data_source["symbol"]

    if not Path(data_path).exists():
        typer.echo(f"Error: Data file not found: {data_path}", err=True)
        raise typer.Exit(1)

    try:
        data = local_ohlcv_csv(data_path, symbol)
    except MissingColumnsError as e:
        typer.echo(f"Error: Failed to load OHLCV data: {e}", err=True)
        raise typer.Exit(1)

    start_date = datetime_range["start"]
    end_date = datetime_range["end"]

    if "datetime" in data.columns:
        data = data[
            (data["datetime"] >= start_date) & (data["datetime"] <= end_date)
        ].copy()
        data = data.sort_values("datetime").reset_index(drop=True)

    registry = FactorRegistry()
    registry.register(MoskowitzMomentumFactor())

    try:
        factor = registry.get(factor_name)
    except Exception:
        typer.echo(f"Error: Unknown factor: {factor_name}", err=True)
        raise typer.Exit(1)

    try:
        factor_output = factor.compute(data)
    except Exception as e:
        typer.echo(f"Error: Factor calculation failed: {e}", err=True)
        raise typer.Exit(1)

    if len(factor_output) == 0:
        typer.echo("Error: Factor produced no output", err=True)
        raise typer.Exit(1)

    required_cols = {"datetime", "symbol", "factor_name", "factor_value", "available_at"}
    if not required_cols.issubset(set(factor_output.columns)):
        typer.echo("Error: Factor output must have columns: datetime, symbol, factor_name, factor_value, available_at", err=True)
        raise typer.Exit(1)

    if "target_position" in factor_output.columns or "signal_binary" in factor_output.columns:
        typer.echo("Error: Factor output must not contain target_position or signal_binary", err=True)
        raise typer.Exit(1)

    valid_mask = ~factor_output["factor_value"].isnull()
    factor_output = factor_output[valid_mask].reset_index(drop=True)

    if len(factor_output) == 0:
        typer.echo("Error: Factor produced no valid output (all rows have insufficient history)", err=True)
        raise typer.Exit(1)

    composer = SignalComposer()
    composer.set_validator(SignalValidator())

    try:
        signal_df = composer.compose(
            factor_output=factor_output,
            datetime=factor_output["datetime"],
            available_at=factor_output["available_at"],
            symbol=factor_output["symbol"].iloc[0] if "symbol" in factor_output.columns else symbol,
            signal_name=signal_name,
            source=source,
            contract_version=signal_contract_version,
            weight_policy=build_signed_unit_weight_policy(cfg) if signal_contract_version == SIGNAL_CONTRACT_V02 else None,
        )
    except (SignalValidationError, ValueError) as e:
        typer.echo(f"Error: Signal composition failed: {e}", err=True)
        raise typer.Exit(1)

    alignment_errors = validate_signal_market_date_alignment(signal_df, factor_output)
    if alignment_errors:
        typer.echo("Error: Signal dates do not match selected market dates.", err=True)
        for err in alignment_errors:
            typer.echo(f"Error: {err}", err=True)
        raise typer.Exit(1)

    output_dir = build_output_path(
        output_config["artifacts_dir"],
        symbol,
        signal_name,
        start_date,
        end_date,
    )

    existing = check_files_exist(output_dir)
    if existing and not overwrite:
        typer.echo(
            "Error: Output files exist. Use --overwrite to replace.",
            err=True,
        )
        typer.echo(f"Existing files: {[str(f) for f in existing]}", err=True)
        raise typer.Exit(1)

    signal_value_stats = {}
    if "factor_value" in factor_output.columns:
        signal_value_stats = {
            "min": float(factor_output["factor_value"].min()) if not factor_output["factor_value"].isnull().all() else None,
            "max": float(factor_output["factor_value"].max()) if not factor_output["factor_value"].isnull().all() else None,
            "mean": float(factor_output["factor_value"].mean()) if not factor_output["factor_value"].isnull().all() else None,
            "null_count": int(factor_output["factor_value"].isnull().sum()),
        }

    signal_binary_stats = {}
    if "signal_binary" in signal_df.columns:
        signal_binary_stats = {
            "value_0_count": int((signal_df["signal_binary"] == 0).sum()),
            "value_1_count": int((signal_df["signal_binary"] == 1).sum()),
            "null_count": int(signal_df["signal_binary"].isnull().sum()),
        }

    timing_rule = "same declared daily trading date as datetime for OHLCV-only daily signal"
    if signal_contract_version == SIGNAL_CONTRACT_V02:
        contract = build_v02_signal_contract(
            signal_name=signal_name,
            source=source,
            factor_name=factor_name,
            parameters=cfg.get("factor_params", {}),
            timing_rule=timing_rule,
            symbols=[symbol],
            datetime_range=(start_date, end_date),
            factor_version=factor.version,
            target_weight_config=target_weight_config,
        )
    else:
        contract = build_signal_contract(
            signal_name=signal_name,
            source=source,
            factor_name=factor_name,
            parameters=cfg.get("factor_params", {}),
            decision_rule="1 if signal_value > 0 else 0",
            timing_rule=timing_rule,
            symbols=[symbol],
            datetime_range=(start_date, end_date),
            row_count=len(signal_df),
            signal_value_stats=signal_value_stats,
            signal_binary_stats=signal_binary_stats,
            symbol=symbol,
            frequency="daily",
            factor_version=factor.version,
        )

    quality_report = build_market_data_quality_report(
        market_data=data,
        dataset_name=data_path,
        source_type="local_ohlcv_csv",
    )

    try:
        export_generated_signal_csv(
            signal_df,
            output_dir,
            signal_contract_version=signal_contract_version,
        )
        export_signal_contract_yaml(contract, output_dir)
        export_data_quality_report(quality_report, output_dir)
    except Exception as e:
        typer.echo(f"Error: Failed to export artifacts: {e}", err=True)
        raise typer.Exit(1)

    typer.echo("Signal artifacts generated successfully:")
    typer.echo(f"  - {output_dir}/signal.csv")
    typer.echo(f"  - {output_dir}/signal_contract.yaml")
    typer.echo(f"  - {output_dir}/data_quality_report.json")


@app.command("export-alphaforge-v02-smoke")
def export_alphaforge_v02_smoke(
    output_dir: Path = typer.Option(
        ...,
        "--output-dir",
        "-o",
        help="Directory where the deterministic AlphaForge v0.2 smoke package will be written",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite existing package files if they already exist",
    ),
) -> None:
    """Export a deterministic v0.2 package that AlphaForge can smoke-test."""
    required_files = (
        "market_data.csv",
        "signal.csv",
        "signal_contract.yaml",
        "data_quality_report.json",
        "manifest.json",
        "README.md",
    )
    existing = [name for name in required_files if (output_dir / name).exists()]
    if existing and not overwrite:
        typer.echo("Error: Output package files already exist. Use --overwrite to replace.", err=True)
        typer.echo(f"Existing files: {existing}", err=True)
        raise typer.Exit(1)

    paths = export_demo_alphaforge_v02_compatibility_package(output_dir)
    summary = {
        "status": "exported",
        "output_dir": str(output_dir),
        "files": sorted(paths.keys()),
        "alpha_forge_command": (
            "python3 -m alphaforge.cli smoke-signalforge-package "
            f"--package {output_dir}"
        ),
    }
    typer.echo(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    app()
