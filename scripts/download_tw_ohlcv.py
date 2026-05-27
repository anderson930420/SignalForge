#!/usr/bin/env python3
"""Download Taiwan-listed daily OHLCV data into SignalForge CSV format.

This script is intentionally outside the SignalForge core package because it
uses yfinance as an optional data-source dependency.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


SIGNALFORGE_OHLCV_COLUMNS = ["datetime", "open", "high", "low", "close", "volume"]


def download_tw_ohlcv(
    *,
    symbol: str,
    start: str,
    end: str,
    output: Path,
    downloader=None,
) -> Path:
    """Download one Taiwan symbol and write SignalForge OHLCV CSV."""
    if downloader is None:
        try:
            import yfinance as yf
        except ImportError as exc:
            raise SystemExit(
                "yfinance is required for live downloads. "
                "Install with: python3 -m pip install yfinance"
            ) from exc

        downloader = yf.download

    df = downloader(symbol, start=start, end=end, auto_adjust=False, progress=False)

    if df.empty:
        raise SystemExit(f"No data downloaded for {symbol}")

    normalized = normalize_yfinance_ohlcv_frame(df)
    output.parent.mkdir(parents=True, exist_ok=True)
    normalized.to_csv(output, index=False)
    return output


def normalize_yfinance_ohlcv_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize yfinance-style output to datetime/open/high/low/close/volume."""
    working = df.copy()

    if isinstance(working.columns, pd.MultiIndex):
        working.columns = working.columns.get_level_values(0)

    working = working.reset_index()

    date_candidates = ["Date", "Datetime", "datetime", "date", "index"]
    date_col = next((col for col in date_candidates if col in working.columns), None)
    if date_col is None:
        date_col = working.columns[0]

    working = working.rename(
        columns={
            date_col: "datetime",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adj_close",
            "Volume": "volume",
        }
    )
    working.columns = [str(column).strip() for column in working.columns]

    missing = [column for column in SIGNALFORGE_OHLCV_COLUMNS if column not in working.columns]
    if missing:
        raise SystemExit(
            f"Missing columns after download: {missing}; "
            f"downloaded columns: {working.columns.tolist()}"
        )

    return working.loc[:, SIGNALFORGE_OHLCV_COLUMNS]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Download Taiwan OHLCV data to SignalForge CSV")
    parser.add_argument("--symbol", required=True, help="Yahoo Finance Taiwan ticker, e.g. 2330.TW")
    parser.add_argument("--start", required=True, help="Start date, e.g. 2020-01-01")
    parser.add_argument("--end", required=True, help="End date, e.g. 2025-01-01")
    parser.add_argument("--output", type=Path, required=True, help="Output CSV path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output = download_tw_ohlcv(
        symbol=args.symbol,
        start=args.start,
        end=args.end,
        output=args.output,
    )
    rows = len(pd.read_csv(output))
    print(f"Wrote {rows} rows to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
