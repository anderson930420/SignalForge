# Moskowitz Momentum Factor

## Type

Capability Specification

## Purpose

Define the Moskowitz Momentum Factor implementation for SignalForge MVP.

## Owner

SignalForge

## Factor Source

Based on Moskowitz, Ostdie, and Wells (2024): "Into the Darkness: An Empirical Investigation of Dark Matter Returns"

## Factor Definition

The Moskowitz Momentum Factor measures the trailing 12-month risk-adjusted return trend, designed to capture persistent price momentum while mitigating short-term reversal effects.

## Calculation Method

### Formula

```
signal_value = (CUMRET_12M - CUMRET_1M) / VOL_1M
```

Where:
- CUMRET_12M = Cumulative return from month t-12 to t-1
- CUMRET_1M = Cumulative return from month t-1
- VOL_1M = Rolling 1-month volatility

### Implementation Details

| Aspect | Specification |
|--------|---------------|
| Lookback period | 252 trading days (~12 months) |
| Short-term lag | 21 trading days (~1 month) |
| Volatility window | 21 trading days |
| Risk adjustment | Divide by 1-month volatility |

### Edge Cases

| Case | Handling |
|------|----------|
| Insufficient history | signal_value = NaN |
| Zero volatility | signal_value = NaN (avoid division by zero) |
| Missing price data | signal_value = NaN for affected periods |

## Output Schema

Returns DataFrame with:

| Column | Type | Description |
|--------|------|-------------|
| signal_value | float | Moskowitz momentum factor value |

## Required Input Columns

- datetime
- close

## Factor Metadata

| Attribute | Value |
|-----------|-------|
| name | "moskowitz_momentum" |
| source | "moskowitz_2024" |

## Rationale

The Moskowitz Momentum Factor captures medium-term price momentum while explicitly controlling for short-term reversal. The risk-adjustment via volatility makes the signal comparable across assets with different volatility regimes.
