# Tasks: End-to-End Example Artifact Generation Test

- [x] Add `tests/test_e2e_generate_artifacts.py` as a real end-to-end CLI regression test.
- [x] Generate deterministic mock OHLCV data with 300+ business-day rows using `pd.bdate_range`.
- [x] Invoke the public `signalforge` CLI root command with `--config` and `--overwrite`.
- [x] Assert `signal.csv`, `signal_contract.yaml`, and `data_quality_report.json` exist in the expected output directory.
- [x] Verify the generated `signal.csv` schema, ordering, binary constraint, datetime constraint, and duplicate constraint.
- [x] Verify the generated `signal_contract.yaml` and `data_quality_report.json` fields match the public contract.
- [x] Run `pytest`, `ruff check .`, and OpenSpec validation successfully.
