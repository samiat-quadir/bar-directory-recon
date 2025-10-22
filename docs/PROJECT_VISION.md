# Project Vision — Bar Directory Recon

## Problem

- Public and professional bar directories drift quickly: contact data, licensing status, and firm affiliations fall out of sync.
- Manual cleanup is slow, inconsistent, and rarely auditable.
- Downstream teams (legal ops, intake, analytics) cannot rely on stale registries for decision making.

## Our Solution

- Provide a focused SDK + CLI that ingests raw registry exports, normalizes them into a stable schema, validates records against configurable rules, scores overall health, and emits reports that can be acted on immediately.
- Lean on the existing `universal_recon` plugin ecosystem so new jurisdictions and formats can be onboarded with minimal code.
- Treat observability as a first-class feature: every run produces summaries, drift indicators, and guard-rail status for CI.

## Primary Users

- **Data quality teams** who reconcile public registries weekly.
- **Analysts and researchers** comparing multiple jurisdictions or time ranges.
- **Automation squads** wiring the pipeline into scheduled routines across devices (Alienware, ASUS, cloud runners).

## What “Good” Looks Like in 90 Days

- A single `bdr` CLI command runs ingest → normalize → validate → score → report on a reference dataset in under 60 seconds.
- Schema, field-map, and validation contracts are documented, versioned, and exercised in CI.
- Drift and quality metrics surface automatically in the weekly insights workflow and guard-health reports.
- SDK primitives are published to TestPyPI with a quickstart notebook demonstrating the end-to-end flow.

## Guiding Principles

- **Small, testable units**: keep transforms pure and deterministic.
- **Composability first**: plugins and adapters must compose without special-casing.
- **Secure by default**: secrets and credentials remain outside of source control; workflows stay pinned to SHAs.
- **Operational excellence**: CI guardrails, ps-lint readiness, and branch hygiene automation remain green while shipping features.
