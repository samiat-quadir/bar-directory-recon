# Deprecated / Legacy Areas

This page enumerates legacy or superseded areas to reduce contributor confusion.

## Directories

- `legacy_intake/` — superseded by the universal pipeline. Keep for historical reference; do **not** add new code here.
- `archive/`, `automation/`, `audits/`, `logs/`, `scratch/`, `device-specific/` — treated as attic; excluded from coverage and CI.

## Tests

- Optional modules (e.g., Hallandale) may be **skipped** when not present; this is intentional for now.

## Policy

- New features should target the universal pipeline and plugin architecture (see `docs/PLUGINS.md`).