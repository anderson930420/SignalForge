# Proposal: Document Daily Datetime Contract

## Change Name

document-daily-datetime-contract

## What

Clarify SignalForge's producer-side daily OHLCV datetime policy in docs and contract metadata.

## Why

AlphaForge now aligns custom daily signals by the declared input calendar date. SignalForge should state the same daily trading-date interpretation so produced `signal.csv` artifacts are handed off without ambiguity around timezone offsets or UTC-shifted instants.

## User Impact

Users and downstream consumers can treat SignalForge MVP daily `datetime` and `available_at` values as declared trading-date labels for daily signal alignment.

## Scope

### In Scope

- README, AlphaForge handoff, and E2E demo documentation.
- Deterministic `timing.available_at_rule` wording for OHLCV-only daily signals.
- Regression tests for the documented policy and timing text.

### Out of Scope

- `signal.csv` schema changes.
- Factor output schema changes.
- Intraday support or event-time availability validation.
- Point-in-time correctness claims for non-OHLCV data.
- AlphaForge imports, backtesting, performance ranking, or portfolio logic.
