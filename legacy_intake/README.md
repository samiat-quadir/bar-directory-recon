# Legacy Intake Documentation
*Generated: August 22, 2025*

## Overview
This directory contains pre-staged legacy fixtures and inventory from C:\Temp sources, designed to support legacy data analysis and testing without including large archives in git.

## Directory Structure
```
legacy_intake/
├── fixtures/          # Sample files (CSV, DB, HTML, HTM)
│   ├── *.csv          # CSV data files
│   ├── *.db           # Database files
│   ├── *.html         # HTML page sources
│   └── *.htm          # HTML files
└── index/
    └── INVENTORY.json # Comprehensive file metadata
```

## Selection Criteria
- **Source Directories**: C:\Temp\{ExtractedZips, DeepDiveExtract, ScriptInsights, DeepDiveChunks, DeepDiveSummary, ZipSummaries, AIPrompts}
- **File Extensions**: .csv, .db, .html, .htm
- **Size Limit**: < 50MB per file (git-friendly)
- **Deduplication**: Files with same names were skipped

## Fixture Statistics
- **Total Files**: 242 samples
- **Total Size**: ~65MB
- **File Types**: Legal data, web scraping results, database exports
- **Date Range**: Various (see INVENTORY.json for details)

## Inventory Features
The `INVENTORY.json` file contains:
- File paths and names
- File sizes and extensions  
- SHA1 hashes (first 2MB for large files)
- Creation and modification timestamps
- Source root tracking
- Metadata about selection process

## Usage
These fixtures can be used for:
- Testing data processing pipelines
- Validating legacy data formats
- Development and debugging
- Sample data for analysis tools

## Maintenance
- Large files (>50MB) are excluded to keep git repository manageable
- Original files remain in C:\Temp for full access
- Inventory provides checksums for integrity verification

Branch: feat/legacy-intake-2025-08-22
Commit: cb408fa