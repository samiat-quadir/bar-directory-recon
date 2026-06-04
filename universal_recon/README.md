# Universal Recon

> ⚠️ **EXPERIMENTAL — NOT PART OF THE PRODUCTION WORKFLOW**
>
> This module is experimental and under active development.
> It is **NOT** part of the supported CSV → Google Sheets export workflow.
>
> **For production use, see the [Golden Path documentation](../docs/soft-launch.md).**

## Overview

Universal Recon is an experimental plugin-based reconnaissance framework for extracting and analyzing data from legal bar directories. It provides modular scrapers, validators, and analytics tools.

## Status

| Component | Status | Notes |
|-----------|--------|-------|
| `core/` | Experimental | Base framework classes |
| `plugins/` | Experimental | Data extraction plugins |
| `scrapers/` | Experimental | Web scraping modules |
| `validators/` | Experimental | Data validation tools |
| `analytics/` | Experimental | Analysis and reporting |
| `sync/` | Experimental | Data synchronization |

## Configuration

This module uses **YAML configuration files** for consistency:
- `config/*.yaml` for plugin and scraper configuration
- JSON files are deprecated and will be migrated to YAML

## Usage

This module is for internal development and testing only. Do not use in production.

```python
# Example (for development only)
from universal_recon import main

# This is NOT the supported workflow
# Use `bdr export csv-to-sheets` instead
```

## Golden Path (Production)

For the supported production workflow, use:

```bash
# The one supported command for CSV → Sheets export
bdr export csv-to-sheets your_leads.csv --sheet-id YOUR_SHEET_ID
```

See [docs/soft-launch.md](../docs/soft-launch.md) for complete setup instructions.

## Development Notes

- All new features should be added to the golden path (`tools/gsheets_exporter.py`)
- Universal recon may be archived or removed in a future release
- Do not reference universal_recon in user-facing documentation

---

Last updated: January 2026
