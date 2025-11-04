# Roadmap — Next Four Weeks

## Week 1: CLI Skeleton & Documentation

- Land `docs/PROJECT_VISION.md`, `docs/ARCHITECTURE.md`, and `docs/INDEX.md` (tonight).
- Ship `scripts/bdr.py` CLI stub with placeholder commands (`ingest`, `normalize`, `validate`, `score`, `report`).
- Prepare demo dataset shell and `make demo` target for quick smoke tests.

## Week 2: Wiring & Contracts

- Wire the CLI stub to existing normalization and validation utilities.
- Finalize schema/field-map/ruleset contracts (`schema.yaml`, `fieldmap.yaml`, `ruleset.yaml`).
- Add fast tests that assert CLI output shape and contract presence.

## Week 3: First Connector & Demo

- Implement the first external connector using the plugin architecture.
- Produce a recorded CLI demo run with artifacts saved to `artifacts/demo/`.
- Introduce snapshot tests for expected CSV/JSON outputs.

## Week 4: Packaging & Observability

- Package the SDK/CLI for TestPyPI along with a quickstart notebook.
- Extend weekly insights with connector health metrics and CLI adoption stats.
- Add optional async execution flag for pilot users (behind feature gate).
