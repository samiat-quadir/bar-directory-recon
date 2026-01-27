# Integrity Guarantees

## Overview

The Bar Directory Recon integrity subsystem provides **OPT-IN** data quality and reliability features for web scraping pipelines. All features default to permissive backward-compatible behavior and require explicit configuration to enable strict validation.

## Core Guarantees

### 1. UTC Timezone Consistency

**Guarantee**: All timestamps use timezone-aware UTC (`datetime.now(timezone.utc)`)

**Impact**:
- Eliminates timezone ambiguity in logs and exports
- Consistent timestamp ordering across systems
- Prevents daylight saving time issues

**Files**:
- `src/logger.py` (9 locations)
- `src/orchestrator.py` (3 locations)

**Verification**: All datetime objects include `+00:00` UTC offset

---

### 2. Output File Collision Prevention

**Guarantee**: No two scraping runs can overwrite the same output file

**Strategies**:
1. **UUID** (default): Appends unique UUID to filename
2. **Millisecond**: Uses millisecond-precision timestamps
3. **Increment**: Auto-increments counter if file exists

**Configuration**:
```python
orchestrator = ScrapingOrchestrator(
    collision_strategy='millisecond'  # or 'uuid', 'increment'
)
```

**Files**:
- `policies/export_policy.py`
- `tests/integrity/test_output_collision.py`

---

### 3. Deduplication Transparency

**Guarantee**: All duplicate removal operations are logged and auditable

**Features**:
- Logs total vs unique counts: `"1000 total URLs → 850 unique (150 duplicates removed)"`
- Exports JSON report to `_deduplication_report.json`
- Preserves original deduplication algorithm

**Files**:
- `reports/deduplication_report.py`
- `tests/integrity/test_deduplication_transparency.py`

**Output Example**:
```json
{
  "total_count": 1000,
  "unique_count": 850,
  "duplicates_removed": 150,
  "deduplication_rate_percent": 85.0
}
```

---

### 4. Empty Result Detection (OPT-IN)

**Guarantee**: Zero URL/record scenarios can be detected and flagged

**Default Behavior**: Logs warning, continues execution (backward-compatible)

**Strict Mode** (OPT-IN):
```python
orchestrator = ScrapingOrchestrator(
    allow_empty_urls=False,    # Raise error if 0 URLs
    allow_empty_records=False  # Raise error if 0 records
)
```

**Features**:
- Configurable warning thresholds for low counts
- Clear error messages with actionable guidance
- Context-aware validation (listing phase vs detail phase)

**Files**:
- `policies/failure_policy.py`
- `tests/integrity/test_empty_result_failure.py`

---

### 5. Validation Score Filtering (OPT-IN)

**Guarantee**: Records below quality threshold can be filtered and audited

**Default Behavior**: No filtering, all records pass (backward-compatible)

**Strict Mode** (OPT-IN):
```python
orchestrator = ScrapingOrchestrator(
    min_validation_score=60.0,  # Require 60% quality score
    export_rejected=True         # Export low-quality records separately
)
```

**Features**:
- Configurable minimum validation score (0-100)
- Separate export for rejected records (audit trail)
- ValidationSummary reporting with failure breakdown

**Files**:
- `policies/validation_policy.py`
- `reports/validation_summary.py`
- `tests/integrity/test_validation_threshold.py`

---

## Safety Mode Preset

For maximum data quality enforcement, use the **MAXIMUM_SAFETY_MODE** preset:

```python
from policies.safety_presets import MAXIMUM_SAFETY_MODE

orchestrator = ScrapingOrchestrator(
    config_path="config.json",
    **MAXIMUM_SAFETY_MODE  # Apply strict validation
)
```

**Preset Configuration**:
- `allow_empty_urls=False` → Fail on 0 URLs
- `allow_empty_records=False` → Fail on 0 records
- `min_validation_score=70.0` → High quality threshold
- `export_rejected=True` → Audit all rejected records
- `collision_strategy='uuid'` → Guaranteed unique filenames

---

## Backward Compatibility

**All integrity features default to permissive behavior:**

| Feature | Default | Strict Mode (OPT-IN) |
|---------|---------|---------------------|
| Empty URLs | Warning logged | ValueError raised |
| Empty records | Warning logged | ValueError raised |
| Validation score | All records pass | Filter by threshold |
| Rejected export | Discarded | Exported to separate file |
| Collision strategy | UUID appended | Configurable |

**Migration Path**: Existing pipelines continue working unchanged. Enable strict features incrementally as needed.

---

## Testing

All integrity features have comprehensive test coverage:

- **UTC**: 3 tests (timezone awareness, orchestrator integration)
- **Export collision**: 11 tests (all strategies, edge cases)
- **Deduplication**: 9 tests (tracking, reporting, integration)
- **Empty result**: 17 tests (permissive/strict modes, thresholds)
- **Validation**: 19 tests (filtering, summary, configuration)

**Total**: 59 dedicated integrity tests

---

## Limitations

See [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) for current constraints and edge cases.

---

## References

- [MAXIMUM_SAFETY_MODE.md](../MAXIMUM_SAFETY_MODE.md) - Preset configuration guide
- [BASELINE.md](../BASELINE.md) - Backward compatibility baseline
- Implementation summary: `INTEGRITY_IMPLEMENTATION_SUMMARY.md`
