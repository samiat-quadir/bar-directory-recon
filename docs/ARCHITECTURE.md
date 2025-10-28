# Architecture Overview

Bar Directory Recon combines a lean SDK with CI-first automation. Responsibilities are split between orchestration utilities in `src/` and the pluggable analytics/validation engine in `universal_recon/`.

## Data Flow (Ingest → Normalize → Validate → Score → Report)

1. **Ingest**

    - Connectors in `universal_recon/plugins/` fetch registry exports (CSV, JSON, HTML).
    - Workflow guard + fast parity workflows prevent expensive runs on workflow-only edits.

1. **Normalize**

    - `universal_recon/utils/record_normalizer.py` maps raw fields to the canonical schema.
    - `src/pagination_manager.py` and `src/data_extractor.py` standardize scraping and batching.

1. **Validate**

    - Rule definitions live in `universal_recon/validators/` (`validator_loader.py`, `validation_matrix.py`).
    - ps-lint burn-in keeps PowerShell automation reliable across devices.

1. **Score & Visualize**

    - `universal_recon/analytics/score_visualizer.py` and overlay helpers surface drift and coverage gaps.
    - Weekly CI insights combine guard drift metrics with cancellation savings.

1. **Report**

    - Artifacts land in `artifacts/` plus issue upserts (guard health, branch hygiene, CI weekly insights).
    - `src/notification_agent.py` prepares notification payloads for downstream teams.

## Module Responsibilities

| Area | Modules | Notes |
| --- | --- | --- |
| Orchestration | `src/orchestrator.py`, `src/property_enrichment.py` | Coordinates run order, enrichment, and retries. |
| Automation | `scripts/*.ps1`, `.github/workflows/*` | Flip kits, guard wiring, ps-lint readiness, drift reporting. |
| Plugins | `universal_recon/plugins/*` | Jurisdiction-specific ingestion and normalization logic. |
| Validation | `universal_recon/validators/*` | Schema rules, field maps, validation matrix loaders. |
| Analytics | `universal_recon/analytics/*` | Drift metrics, scoring, overlay visualization, summaries. |
| Utilities | `universal_recon/utils/*`, `src/utils/*` | Shared helpers for HTTP, pagination, serialization. |

## Cross-Cutting Concerns

- **Observability**: Guard health audit, weekly insights, and ps-lint readiness summaries keep signal high in CI.
- **Security**: Branch protection enforces audit + fast tests + workflow guard; Actions stay pinned to SHAs; secrets remain external.
- **Cross-device**: Bootstrap bundles and validation scripts maintain parity for ASUS, Alienware, and GitHub-hosted runners.
- **Extensibility**: New connectors implement the ingest + normalize contract and automatically inherit validation + scoring behaviors.
