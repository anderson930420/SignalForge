# Design: AlphaForge Compatibility Smoke Export Package

## Overview

The smoke export package is a static, deterministic example bundle that documents the exact artifact set AlphaForge should be able to consume.

It is intentionally narrow:

`market_data.csv` -> `signal.csv` -> `signal_contract.yaml` -> `data_quality_report.json` -> `manifest.json` -> `README.md`

## Design Goals

- Make the SignalForge/AlphaForge boundary explicit
- Provide a stable example directory and file set
- Keep AlphaForge out of SignalForge runtime and tests
- Preserve compatibility semantics without adding new dependencies

## Package Semantics

- `market_data.csv` anchors the reference market data window
- `signal.csv` contains the AlphaForge-consumable signal rows
- `signal_contract.yaml` records provenance and contract metadata
- `data_quality_report.json` records package-level quality metadata
- `manifest.json` ties the bundle together for deterministic review
- `README.md` explains how AlphaForge should consume the bundle

## Boundary Notes

The package must prove interoperability, not integration. SignalForge remains responsible for producing the bundle and validating schema expectations. AlphaForge remains the validation and backtest backend.

## Non-Goals

- No AlphaForge imports
- No AlphaForge dependency declarations
- No runtime export refactor
- No new test coverage in this change
