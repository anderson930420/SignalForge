# Signal Export Contract

## Type

Capability Specification

## Purpose

Define the export pipeline that writes signal artifacts to disk with deterministic layout.

## Owner

SignalForge

## Component Location

`export.py` owns artifact writing and deterministic file layout.

## Export Artifacts

SignalForge exports three artifacts for every signal generation run:

| Artifact | Format | Filename |
|----------|--------|----------|
| Signal data | CSV | signal.csv |
| Signal contract | YAML | signal_contract.yaml |
| Data quality report | JSON | data_quality_report.json |

## Directory Structure

Artifacts are written to the configured artifacts directory with this deterministic layout:

```
{artifacts_dir}/
└── {symbol}/
    └── {datetime_range_start}_{datetime_range_end}/
        ├── signal.csv
        ├── signal_contract.yaml
        └── data_quality_report.json
```

## Export Rules

### signal.csv Export

- Use specified column order from signal-artifact-contract
- No index column
- UTF-8 encoding
- Line terminator: Unix (LF)

### signal_contract.yaml Export

- Follow signal-contract-yaml schema
- Non-empty signals list
- Accurate statistics

### data_quality_report.json Export

- Follow data-quality-report schema
- All quality metrics populated
- Issues list accurate

## Determinism

Given the same input data and factor configuration, export must produce byte-for-byte identical artifacts.

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Write permission denied | Raise ExportError |
| Disk full | Raise ExportError |
| Invalid data | Raise ExportError with details |

## Testing Requirements

- Export produces all three artifacts
- signal.csv has correct column order
- signal_contract.yaml is valid YAML
- data_quality_report.json is valid JSON
- Export is deterministic
