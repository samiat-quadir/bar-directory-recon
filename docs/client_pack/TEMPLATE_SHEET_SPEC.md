# Google Sheet Template Specification

A lean spec for clients building their export target Google Sheet before running `bdr export csv-to-sheets`.

## Overview

The target Google Sheet needs one primary worksheet with columns that map to your CSV headers. The spec below ensures zero-configuration exports.

## Worksheet Structure

| Aspect | Requirement | Note |
|--------|-------------|------|
| **Worksheet Name** | "leads" (default) or custom via `--worksheet` | Case-sensitive |
| **Row 1** | Column headers (must match CSV headers) | Headers in exact CSV column order |
| **Data Start** | Row 2 | Row 1 reserved for headers |
| **Column Order** | Match the CSV column order | No reordering during import |
| **Data Types** | All TEXT (recommended) | Avoid pre-formatted numbers/dates |

## Column Definition Template

Create one column for each field in your CSV. Example for a "bar attorney leads" export:

| Column | Header | Type | Example |
|--------|--------|------|---------|
| A | Name | TEXT | John Doe |
| B | Email | TEXT | john@example.com |
| C | Phone | TEXT | 555-123-4567 |
| D | Firm | TEXT | Smith & Associates |
| E | Jurisdiction | TEXT | California |
| F | Practice Area | TEXT | Corporate Law |

### Header Naming Rules

- **Match CSV exactly**: If CSV has `Attorney Name`, header must be `Attorney Name` (case-sensitive)
- **No special characters**: Use underscores or spaces, avoid `#`, `@`, `$`
- **Unique headers**: No duplicate column names
- **ASCII preferred**: Avoid emoji or non-Latin characters

## Sheet Organization (Optional)

For larger workbooks, use these optional tabs:

| Tab Name | Purpose | Auto-created? |
|----------|---------|---------------|
| "leads" (primary) | Incoming/updated records | No—create manually |
| "archive" | Historical records (manual reference) | No |
| "error_log" | Failed rows from last run (if using update-only mode) | No—created by tool if `--log-errors` enabled |

## Pre-Export Checklist

- [ ] Worksheet named exactly "leads" (or confirmed with `--worksheet <name>`)
- [ ] Header row (Row 1) matches all CSV columns in order
- [ ] No formula-based headers (plain text only)
- [ ] Sheet shared with Service Account email with Editor access
- [ ] Column format set to TEXT (automatic for most columns)

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Header row missing | Columns skipped, data misaligned | Add Row 1 with headers before running export |
| Headers don't match CSV | Export fails or maps wrongly | Run `bdr doctor` to validate, then fix headers |
| Sheet not shared | Permission denied on write | Share sheet with Service Account email (Editor) |
| Wrong worksheet name | Export targets wrong tab | Use `--worksheet <exact_name>` or rename to "leads" |
| Merged cells in header row | Parser confusion | Unmerge cells before export |

## Dedupe & Updates

If using `--dedupe-key <column>` or `--mode update-only`:

- **Dedupe Key** must be a TEXT column with unique, stable values (e.g., Email, ID)
- **Update-only mode** requires `--dedupe-key` pointing to a column with no nulls
- **Append mode** (default) ignores dedupe and appends all rows as new

## Example: Minimal Sheet Setup

```
leads (worksheet)
├─ Row 1:     Name         Email               Phone         Firm
├─ Row 2:     John Doe     john@example.com    555-123-4567  Smith LLC
├─ Row 3:     Jane Smith   jane@example.com    555-987-6543  Jones PC
└─ (more rows)
```

Then run:
```bash
bdr export csv-to-sheets data.csv --sheet-id <ID> --worksheet leads
```

---

**Questions?** See [TROUBLESHOOTING_ONE_PAGE.md](TROUBLESHOOTING_ONE_PAGE.md) or contact support.
