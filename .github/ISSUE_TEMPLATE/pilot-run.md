---
name: Pilot Run Execution
about: Track a pilot integration run following the PILOT_RUN_SOP
title: "Pilot Run: [Your Organization Name]"
labels: ["pilot", "ops"]
assignees: []
---

## Pilot Run Checklist

**Organization**: [Your org name here]  
**Pilot Contact**: [Name + email]  
**Start Date**: [YYYY-MM-DD]  
**Expected Completion**: [YYYY-MM-DD]

---

### Phase 1: Pre-Run Setup

- [ ] **Intake Complete**: CSV data file prepared (headers + rows validated)
- [ ] **Google Sheet Shared**: Sheet URL and Sheet ID provided to bar-directory-recon team
- [ ] **Deduplication Key Identified**: Column name chosen or "none" if all rows unique
- [ ] **Credentials Configured**: Service account key in `GOOGLE_SHEETS_CREDENTIALS_PATH`

**Notes on Phase 1**:
```
[Add any setup blockers or questions here]
```

---

### Phase 2: Validation Checks

- [ ] **Doctor Pass**: `bdr doctor --no-exec` completed successfully
- [ ] **Safe-Run Completed**: `--safe-mode` export run to preview data (no write)
- [ ] **Safe-Run Report Reviewed**: Row counts, columns, and data shape verified

**Safe-Run Report Summary**:
```
Expected rows: [N]
Preview columns: [column names]
Any warnings/errors: [None / describe]
```

---

### Phase 3: Production Export

- [ ] **Append Run Completed**: `--mode append` export executed
- [ ] **Google Sheets Verified**: Data visible in sheet, no truncation or encoding issues
- [ ] **Row Count Validated**: Confirmed >= CSV row count (accounting for dedup)
- [ ] **Performance Acceptable**: Command runtime < 30s

**Export Summary**:
```
Command used (sanitized): bdr export csv-to-sheets [file] --sheet-id [REDACTED] --mode append
Rows uploaded: [count]
Runtime: [seconds]
Any errors/warnings: [None / describe]
```

---

### Phase 4: Sign-Off

- [ ] **Data Quality Approved**: All columns present, no artifacts, data matches source
- [ ] **Support Bundle Collected** (if issues occurred): Error logs and support packet gathered
- [ ] **Next Steps Agreed**: Production schedule or rollback decision documented

**Sign-Off Notes**:
```
✅ Pilot validation: [PASS / NEEDS REWORK / BLOCKED]
Issues encountered: [None / list]
Recommended next action: [Move to production / Needs refinement / Hold]
```

---

## Troubleshooting & Support

If you encounter issues, please provide:

**Error Details**:
- Full error message from console
- Command used (sanitize any sensitive IDs)
- `bdr --version` output
- Last 20–30 lines from log file (if available)

**Data Sample** (if safe to share):
- CSV header row
- CSV row count (`wc -l` or PowerShell `Measure-Object`)
- Sample row that caused error (if applicable)

**Related Documentation**:
- [Pilot Run SOP](../../docs/ops/PILOT_RUN_SOP.md)
- [CSV-to-Sheets Usage Guide](../../docs/usage/csv-to-sheets.md)
- [Google Sheets Setup](../../docs/setup/gsheets.md)

---

## Contact & Escalation

- **Questions**: Comment on this issue
- **Urgent**: Mention @samiat-quadir
- **Documentation Issues**: Link to specific section in docs/

---

**Last Updated**: 2026-02-03
