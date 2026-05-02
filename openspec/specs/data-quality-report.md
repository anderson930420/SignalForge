# Data Quality Report

## Type

Capability Specification

## Purpose

Define the schema and generation rules for data_quality_report.json artifacts.

## Owner

SignalForge

## Artifact Location

data_quality_report.json is co-located with signal.csv and signal_contract.yaml in the artifacts directory.

## JSON Schema

```json
{
  "version": "string",
  "exported_at": "ISO 8601 timestamp",
  "generator": "SignalForge",
  "data_source": {
    "symbol": "string",
    "datetime_range": {
      "start": "ISO 8601 timestamp",
      "end": "ISO 8601 timestamp"
    },
    "row_count": "integer"
  },
  "quality_metrics": {
    "ohlcv_completeness": {
      "open_null_count": "integer",
      "high_null_count": "integer",
      "low_null_count": "integer",
      "close_null_count": "integer",
      "volume_null_count": "integer",
      "total_rows": "integer"
    },
    "price_integrity": {
      "high_low_violations": "integer",
      "high_open_violations": "integer",
      "low_open_violations": "integer"
    },
    "temporal_integrity": {
      "duplicate_timestamps": "integer",
      "missing_bars": "integer"
    }
  },
  "issues": [
    {
      "severity": "warning | error",
      "code": "string",
      "message": "string",
      "affected_rows": "integer"
    }
  ]
}
```

## Required Fields

- version: Required
- exported_at: Required
- generator: Required, must be "SignalForge"
- data_source: Required
- quality_metrics: Required
- issues: Required, may be empty list

## Severity Levels

| Level | Description |
|-------|-------------|
| warning | Data quality issue that does not prevent signal generation |
| error | Data quality issue that may affect signal validity |

## Issue Codes

| Code | Description |
|------|-------------|
| NULL_OHLCV | Null values present in OHLCV columns |
| PRICE_INTEGRITY_VIOLATION | Price relationship violated (high < low, etc.) |
| DUPLICATE_TIMESTAMP | Duplicate timestamps found and deduplicated |
| MISSING_BARS | Expected bars missing from datetime range |

## Constraints

- total_rows must equal row_count from data_source
- high_low_violations + high_open_violations + low_open_violations must be >= 0
- issues list may be empty
