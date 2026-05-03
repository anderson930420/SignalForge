"""CLI for SignalForge signal generation."""

from pathlib import Path

import typer

from signalforge.data_registry import local_ohlcv_csv
from signalforge.factor_registry import FactorRegistry
from signalforge.factors.moskowitz_momentum import MoskowitzMomentumFactor
from signalforge.schemas import MissingColumnsError, SignalValidationError
from signalforge.signal_composer import SignalComposer
from signalforge.export import (
    export_signal_csv,
    export_signal_contract_yaml,
    export_data_quality_report,
    build_signal_contract,
    build_data_quality_report,
)


app = typer.Typer(help="SignalForge - Paper-derived factor and standardized signal generation layer")


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
    start_date: str,
    end_date: str,
) -> Path:
    """Build deterministic output path."""
    start_clean = start_date.replace("-", "")
    end_clean = end_date.replace("-", "")
    return Path(artifacts_dir) / symbol / f"{start_clean}_{end_clean}"


def check_files_exist(output_dir: Path) -> list[Path]:
    """Check which required files already exist."""
    files = [
        output_dir / "signal.csv",
        output_dir / "signal_contract.yaml",
        output_dir / "data_quality_report.json",
    ]
    return [f for f in files if f.exists()]


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
        ]

    registry = FactorRegistry()
    registry.register(MoskowitzMomentumFactor())

    try:
        factor = registry.get(factor_name)
    except Exception:
        typer.echo(f"Error: Unknown factor: {factor_name}", err=True)
        raise typer.Exit(1)

    try:
        factor_output = factor.calculate(data)
    except Exception as e:
        typer.echo(f"Error: Factor calculation failed: {e}", err=True)
        raise typer.Exit(1)

    composer = SignalComposer()
    composer.set_validator(SignalValidator())

    if len(factor_output) == 0:
        typer.echo("Error: Factor produced no output", err=True)
        raise typer.Exit(1)

    first_row = factor_output.iloc[0]
    first_datetime = data.iloc[0]["datetime"] if "datetime" in data.columns else first_row.get("datetime", start_date)
    available_at = first_datetime

    try:
        signal_df = composer.compose(
            factor_output=factor_output,
            datetime=first_datetime,
            available_at=available_at,
            symbol=symbol,
            signal_name=signal_name,
            source=source,
        )
    except SignalValidationError as e:
        typer.echo(f"Error: Signal composition failed: {e}", err=True)
        raise typer.Exit(1)

    output_dir = build_output_path(
        output_config["artifacts_dir"],
        symbol,
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

    contract = build_signal_contract(
        signal_name=signal_name,
        source=source,
        factor_name=factor_name,
        parameters=cfg.get("factor_params", {}),
        decision_rule="signal_binary = 1 if signal_value > 0 else 0",
        timing_rule="available_at <= datetime",
        symbols=[symbol],
        datetime_range=(start_date, end_date),
        row_count=len(signal_df),
        signal_value_stats=signal_value_stats,
        signal_binary_stats=signal_binary_stats,
    )

    quality_report = build_data_quality_report(
        signal_df=signal_df,
        dataset_name=data_path,
        source_type="csv",
    )

    try:
        export_signal_csv(signal_df, output_dir, validate=True)
        export_signal_contract_yaml(contract, output_dir)
        export_data_quality_report(quality_report, output_dir)
    except Exception as e:
        typer.echo(f"Error: Failed to export artifacts: {e}", err=True)
        raise typer.Exit(1)

    typer.echo("Signal artifacts generated successfully:")
    typer.echo(f"  - {output_dir}/signal.csv")
    typer.echo(f"  - {output_dir}/signal_contract.yaml")
    typer.echo(f"  - {output_dir}/data_quality_report.json")


if __name__ == "__main__":
    app()