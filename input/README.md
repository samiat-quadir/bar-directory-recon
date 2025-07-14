# Input Directory

This directory contains automatically downloaded property lists and inspection documents from various municipal sources.

## File Naming Convention

Downloaded files follow this pattern:

```
{original_name}_{timestamp}_{source}.{extension}
```

Examples:

- `inspection_list_20250709_120000_miami_dade.pdf`
- `recertification_report_20250709_120000_broward.xlsx`
- `property_safety_list_20250709_120000_palm_beach.pdf`

## Sources

Files are automatically downloaded from configured municipal websites including:

- Miami-Dade County property and inspection records
- Broward County building safety programs
- Palm Beach County recertification lists

## Processing

After download, files in this directory should be processed using:

1. `python src/data_hunter.py` - For discovery and download
2. `python unified_scraper.py --pdf input/filename.pdf` - For processing
3. `python final_hallandale_pipeline.py` - For enrichment (adapt for other cities)

## Automated Cleanup

Old files (30+ days) may be automatically archived to prevent directory bloat.
