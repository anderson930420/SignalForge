# harden-declared-trading-date-normalization

## Summary

Apply SignalForge's declared daily trading-date policy to compatibility helpers and AlphaForge compatibility package validation.

## Motivation

SignalForge v0.1.2 documents MVP daily `datetime` and `available_at` fields as declared trading-date labels. Some helper paths still parse with `utc=True` before extracting or comparing daily dates, which can shift offset timestamps to a previous UTC calendar date. For example, `2025-01-02T00:00:00+08:00` must align to declared trading date `2025-01-02`, not `2025-01-01`.

## Scope

- Add a reusable declared daily trading-date normalization helper.
- Update signal/market alignment validation to compare declared daily dates.
- Update AlphaForge compatibility package normalization and readback validation to preserve declared daily dates.
- Add regression tests for offset timestamp alignment, `available_at` daily-date validation, package output, and invalid datetime handling.

## Non-Goals

- No signal schema changes.
- No `signal_contract.yaml` schema shape changes.
- No AlphaForge code changes or imports.
- No intraday timing validation.
- No backtesting, portfolio logic, or performance ranking.
