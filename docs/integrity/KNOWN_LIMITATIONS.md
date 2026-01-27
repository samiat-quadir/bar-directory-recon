# Known Limitations

## Overview

This document outlines current limitations, edge cases, and known constraints of the integrity subsystem. These are areas where behavior may be unexpected or where additional development is needed.

---

## 1. Validation Score Source

**Limitation**: The integrity subsystem does **NOT** implement validation scoring logic.

**Details**:
- `ValidationPolicy.filter_by_validation_score()` expects records to **already have** a `validation_score` field
- The orchestrator or data extractors must compute scores before filtering
- Missing `validation_score` fields are treated as score = 0.0

**Impact**: Records without scores will be rejected in strict mode (if min_score > 0)

**Workaround**: Ensure validation scoring is implemented in data extraction pipeline before enabling threshold filtering.

**Future Work**: Consider adding default scoring heuristics (e.g., completeness-based scoring)

---

## 2. Deduplication Algorithm

**Limitation**: Deduplication transparency does **NOT** modify the underlying deduplication algorithm.

**Details**:
- Uses existing simple set-based deduplication (`list(set(urls))`)
- Does not detect semantic duplicates (e.g., `http://example.com` vs `https://example.com/`)
- Order of deduplicated items is non-deterministic (set randomization)

**Impact**: 
- URL normalization issues may cause duplicates to slip through
- Order-dependent pipelines may produce inconsistent results

**Workaround**: Pre-normalize URLs before deduplication (e.g., strip trailing slashes, lowercase)

**Future Work**: Implement URL normalization and semantic duplicate detection

---

## 3. Empty Result Context

**Limitation**: Empty result validation does not distinguish between "no results found" and "scraping failure"

**Details**:
- Both legitimate empty pages and scraping failures produce 0 URLs/records
- Policy cannot differentiate between:
  - A page with genuinely no listings
  - A page where selectors failed to match

**Impact**: Strict mode may raise false-positive errors on legitimately empty pages

**Workaround**: 
- Use permissive mode (default) for exploratory scraping
- Enable strict mode only for known-populated sources
- Monitor logs for low-count warnings even in permissive mode

**Future Work**: Add selector health checks to detect scraping failures independently

---

## 4. Collision Strategy Scope

**Limitation**: Collision prevention only applies to **orchestrator-generated** output files

**Details**:
- `ExportPolicy` collision strategies protect files written by orchestrator
- Does not apply to:
  - User-generated files
  - Plugin output files
  - Log files
  - Intermediate/temporary files

**Impact**: External processes can still overwrite files

**Workaround**: Ensure all file-writing code uses orchestrator's export methods

**Future Work**: Extend collision prevention to all file I/O operations

---

## 5. ValidationSummary Persistence

**Limitation**: ValidationSummary is in-memory only and not automatically persisted

**Details**:
- Summary statistics are lost when orchestrator object is destroyed
- No automatic export to disk/database
- Must manually call `summary.get_summary_dict()` and save

**Impact**: Validation statistics unavailable after script completes

**Workaround**: Explicitly export summary in finally block:
```python
try:
    orchestrator.run()
finally:
    with open("validation_summary.json", "w") as f:
        json.dump(orchestrator.validation_summary.get_summary_dict(), f)
```

**Future Work**: Auto-export validation summary to output directory

---

## 6. Threshold Granularity

**Limitation**: Validation threshold is global and applies uniformly to all records

**Details**:
- Single `min_validation_score` value for entire pipeline
- Cannot have different thresholds for different record types
- Cannot apply progressive thresholds (e.g., stricter as data ages)

**Impact**: Difficult to handle heterogeneous data quality requirements

**Workaround**: Run separate orchestrator instances with different policies per record type

**Future Work**: Support per-field or per-record-type validation policies

---

## 7. Rejected Record Format

**Limitation**: Rejected records are exported in the same format as passed records

**Details**:
- No additional metadata about rejection reason
- No validation score included in rejected export
- Cannot reconstruct why specific records were rejected

**Impact**: Limited auditability of rejection decisions

**Workaround**: Parse validation_summary.json to correlate rejection counts with reasons

**Future Work**: Enrich rejected records with metadata:
```json
{
  "original_record": {...},
  "validation_score": 45.0,
  "rejection_reason": "below_threshold",
  "threshold": 60.0
}
```

---

## 8. Timezone Display

**Limitation**: UTC timestamps may be less readable for users in other timezones

**Details**:
- All timestamps use UTC (`+00:00`) for consistency
- No automatic conversion to local timezone for display
- Users must manually convert if local time is needed

**Impact**: Logs and exports show UTC time, which may differ from user's local time

**Workaround**: Use timezone-aware datetime parsing when reading exports

**Future Work**: Add optional local timezone display in logging while preserving UTC storage

---

## 9. Pre-commit Stash Behavior

**Limitation**: Pre-commit hooks may auto-format files, causing staging confusion

**Details**:
- Black, isort, autoflake hooks run on pre-push (not pre-commit)
- Blocking hooks (secrets, YAML, large files) run on pre-commit
- If formatting changes files, they must be re-staged

**Impact**: Workflow interruption if files are modified by formatters

**Workaround**: 
```bash
git add -A          # Stage all changes
git commit -m "..."  # Commit
# If hooks modified files:
git add -A          # Re-stage formatted files
git commit --amend --no-edit
```

**Future Work**: Configure pre-commit to auto-stage formatted files

---

## 10. Test Coverage Gaps

**Limitation**: Integration tests between policies and orchestrator are minimal

**Details**:
- Policies are well-tested in isolation (59 tests)
- Orchestrator integration is limited
- End-to-end scenarios with multiple policies active are untested

**Impact**: Unknown behavior when multiple strict policies interact

**Workaround**: Test policy combinations manually in staging environment

**Future Work**: Add integration test suite covering policy interactions

---

## Non-Issues (False Alarms)

### ✅ "Validation score filtering might break pipelines"
**Status**: NOT A LIMITATION - Default is permissive (min_score=0, no filtering)

### ✅ "Empty result detection will cause errors"
**Status**: NOT A LIMITATION - Default is permissive (allow_empty=True, warning only)

### ✅ "UUID collision strategy might be slow"
**Status**: NOT A LIMITATION - UUID generation is <1ms, negligible overhead

---

## Reporting Issues

If you encounter limitations not documented here, please:

1. Check if issue is reproducible with default (permissive) configuration
2. Verify behavior with strict mode enabled
3. File issue with:
   - Exact configuration used
   - Expected vs actual behavior
   - Relevant logs/error messages

---

## Version

**Documented**: January 2026  
**Subsystem Version**: 1.0.0 (Initial Release)
