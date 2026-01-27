# Integrity Gaps Workstream — PR Landing Plan

**Document Purpose**: Formalize the PR sequencing, safety requirements, and coverage ratchet strategy for the integrity gap enforcement series.

**Published**: 2026-01-27  
**Status**: ACTIVE  

---

## 1. PR Landing Order

This section specifies the order in which integrity gap PRs must land on main, the required checks for each, and any blockers.

### PR1: Validation Threshold Enforcement

**Feature**: Enforce min validation score; optionally export rejected records.

**Flags/Config**:
- `--min-validation-score` (CLI flag, default: 0.0 — no enforcement)
- `--export-rejected-records` (CLI flag, default: false — no extra output)

**Default Behavior**: 
- ✅ Backward compatible — no filtering unless explicitly enabled
- Existing workflows unchanged
- Records with low scores are still exported if threshold not set

**Required Checks**:
- [x] Unit tests in `tests/integrity/test_validation_threshold.py` (10 tests)
- [x] Integration test in `tests/integrity/test_orchestrator_validation.py` (boundary cases)
- [x] Docs in `docs/integrity/INTEGRITY_GUARANTEES.md` (validation guarantee documented)
- [x] Docs in `docs/integrity/KNOWN_LIMITATIONS.md` (score calculation limitations noted)
- [x] No new required dependencies
- [x] All existing tests passing

**Merge Criteria**:
- Linter: ✅ flake8, mypy, ruff pass
- Test: ✅ Coverage >= 21% (no regression)
- Security: ✅ Bandit, pip-audit pass
- Integration: ✅ install-smoke passes

**Files Changed** (estimate):
- `src/policies/validation_policy.py` (new)
- `src/orchestrator.py` (add validation call in _save_results)
- `tests/integrity/test_validation_threshold.py` (new, 10 tests)
- `docs/integrity/INTEGRITY_GUARANTEES.md` (updated)

---

### PR2: Empty-Result Fail-Fast

**Feature**: Exit with error (not silent success) when extraction yields 0 URLs or 0 records.

**Flags/Config**:
- `--allow-empty-results` (CLI flag, default: true — backward compatible, allow empty)
- `--min-url-count` (CLI flag, default: 0 — threshold for warning)

**Default Behavior**:
- ✅ Backward compatible — allows empty results by default
- Existing workflows unchanged
- Must explicitly set `--allow-empty-results=false` to enable fail-fast

**Required Checks**:
- [x] Unit tests in `tests/integrity/test_empty_result_failure.py` (11 tests)
- [x] Integration test for orchestrator phases (run_listing_phase, run_detail_phase)
- [x] Docs in `docs/integrity/INTEGRITY_GUARANTEES.md` (empty result guarantee documented)
- [x] Config schema updated if using config file (optional)
- [x] All existing tests passing

**Merge Criteria**:
- Linter: ✅ flake8, mypy, ruff pass
- Test: ✅ Coverage >= 21% (no regression)
- Security: ✅ Bandit, pip-audit pass
- Integration: ✅ install-smoke passes

**Files Changed** (estimate):
- `src/policies/failure_policy.py` (new)
- `src/orchestrator.py` (add empty check in run_listing_phase, run_detail_phase)
- `tests/integrity/test_empty_result_failure.py` (new, 11 tests)
- `docs/integrity/INTEGRITY_GUARANTEES.md` (updated)

---

### PR3: Output Collision Prevention

**Feature**: Prevent overwriting output files when multiple runs occur rapidly (same second).

**Flags/Config**:
- `--collision-strategy` (CLI flag, options: `uuid` | `millisecond` | `increment`, default: `uuid` — safe, non-breaking)

**Default Behavior**:
- ✅ Backward compatible — UUID strategy preserves file uniqueness without breaking scripts
- Existing workflows unaffected (different filenames, but still written to correct location)
- No behavior change to output content

**Required Checks**:
- [x] Unit tests in `tests/integrity/test_output_collision.py` (11 tests)
- [x] Integration test for _save_results (verify UUID, ms, increment strategies)
- [x] Docs in `docs/integrity/INTEGRITY_GUARANTEES.md` (collision prevention guarantee)
- [x] Docs in `docs/integrity/KNOWN_LIMITATIONS.md` (note that UUID changes filenames)
- [x] All existing tests passing

**Merge Criteria**:
- Linter: ✅ flake8, mypy, ruff pass
- Test: ✅ Coverage >= 21% (no regression)
- Security: ✅ Bandit, pip-audit pass
- Integration: ✅ install-smoke passes

**Files Changed** (estimate):
- `src/policies/export_policy.py` (new)
- `src/orchestrator.py` (integrate into _save_results)
- `tests/integrity/test_output_collision.py` (new, 11 tests)
- `docs/integrity/INTEGRITY_GUARANTEES.md` (updated)

---

### PR4: Deduplication Transparency

**Feature**: Track and log the number of duplicates removed (not silent dedup).

**Flags/Config**:
- `--dedupe-report-file` (CLI flag, default: none — no report by default)
- `--dedupe-verbose` (CLI flag, default: false — silent unless enabled)

**Default Behavior**:
- ✅ Backward compatible — deduplication still runs the same way
- Adds optional logging only; does not change output content
- Report file only written if explicitly requested

**Required Checks**:
- [x] Unit tests in `tests/integrity/test_deduplication_transparency.py` (10 tests)
- [x] Integration test for deduplicate_with_tracking wrapper
- [x] Docs in `docs/integrity/INTEGRITY_GUARANTEES.md` (dedup transparency guarantee)
- [x] Docs note in `docs/integrity/KNOWN_LIMITATIONS.md` (note that report is async/best-effort)
- [x] All existing tests passing

**Merge Criteria**:
- Linter: ✅ flake8, mypy, ruff pass
- Test: ✅ Coverage >= 21% (no regression)
- Security: ✅ Bandit, pip-audit pass
- Integration: ✅ install-smoke passes

**Files Changed** (estimate):
- `src/reports/deduplication_report.py` (new)
- `src/orchestrator.py` (wrap dedup call with tracking wrapper)
- `tests/integrity/test_deduplication_transparency.py` (new, 10 tests)
- `docs/integrity/INTEGRITY_GUARANTEES.md` (updated)

---

### PR5: Timezone-Aware Timestamps (UTC)

**Feature**: Replace naive `datetime.now()` with UTC-aware timestamps throughout the system.

**Flags/Config**:
- No flags — this is a fix, not a toggle
- UTC is the standard; no option to prefer local time

**Default Behavior**:
- ✅ Backward compatible — timestamps now include timezone info (ISO 8601)
- Logs and exports now contain UTC offset (+00:00)
- No functional change to behavior, only log format improvement

**Required Checks**:
- [x] Unit tests in `tests/integrity/test_timezone_aware.py` (8 tests)
- [x] Integration test for logger (verify UTC in test logs)
- [x] Docs in `docs/integrity/INTEGRITY_GUARANTEES.md` (timestamp guarantee: UTC)
- [x] All existing tests passing (no timezone-naive comparisons broken)

**Merge Criteria**:
- Linter: ✅ flake8, mypy, ruff pass
- Test: ✅ Coverage >= 21% (no regression)
- Security: ✅ Bandit, pip-audit pass
- Integration: ✅ install-smoke passes

**Files Changed** (estimate):
- `src/logger.py` (replace naive datetime.now with UTC-aware)
- `src/orchestrator.py` (one instance of datetime.now → datetime.now(timezone.utc))
- `tests/integrity/test_timezone_aware.py` (new, 8 tests)
- `tests/test_orchestrator.py` (update any timezone-naive mocks)
- `docs/integrity/INTEGRITY_GUARANTEES.md` (updated)

---

## 2. Merge Safety Requirements

### Pre-Merge Safety Checks

For **every PR in this series**:

1. **Branch Hygiene**
   - Branch must be cut from `main` or the previous PR's merge commit
   - No direct commits to `main` during this workstream
   - Rebase on main if conflicts detected (do NOT force-merge)

2. **Automated Checks** (must be green before merge)
   - `fast-tests` (pytest on Python 3.11, coverage >= 21%)
   - `lint` (ruff, mypy, flake8)
   - `audit` (bandit, pip-audit)
   - `ci-workflow-guard` (no workflow changes)

3. **Manual Verification**
   - [ ] All integrity tests in `tests/integrity/` pass
   - [ ] No import errors on sys.path (check with `python -c "import policies; import reports"`)
   - [ ] Backward compatibility verified (run with old config, should work)
   - [ ] Docs are accurate (no broken links, correct flag names)

4. **Conflict Resolution**
   - If conflicts with other PRs: coordinate, do NOT brute-force rebase
   - Contact the repo maintainer (Ali) before force-pushing
   - If conflicts with main: rebase cleanly, re-run full test suite

5. **Code Review Gate**
   - Minimum 1 approval from maintainer
   - Codeowner approval (if applicable)
   - No unresolved comments

### Merge Command (GitHub UI)
```
Click "Squash and merge" or "Create a merge commit" (your choice)
Commit message: "feat(integrity): <description> — <PR-type>"
```

### Post-Merge Verification
After each PR merges:
1. Wait for CI to run on main
2. Verify all required checks pass
3. Check that coverage has not regressed
4. Spot-check the merged code in main

---

## 3. Coverage Ratchet Plan

### Strategy

The integrity workstream is expected to add ~36-50 new unit tests spanning 5 PRs. This will improve overall coverage **after all PRs merge**, not during the workstream.

**Current gate**: 21% (set in PR #352)

### Ratchet Phases

| Phase | Trigger | Action | Notes |
|-------|---------|--------|-------|
| **Current** | Baseline | Gate: 21% | Enforced in CI (pyproject.toml) |
| **Post-PR1-4** | After PR4 merges | Evaluate coverage % | Check CI run on main after PR4 merge |
| **Decision Point** | If coverage >= 23% | Raise gate to 23% | Create PR: `chore/raise-coverage-gate-23` |
| **Decision Point** | If coverage >= 25% | Raise gate to 25% | Create PR: `chore/raise-coverage-gate-25` |
| **Target** | Q2 2026 | Gate: 25% | Gradual ratchet, no mid-workstream jumps |

### Implementation

**Do NOT raise coverage gates mid-workstream** (i.e., after PR1, PR2, PR3 individually).

**After all integrity PRs land** (PR1-5 merged to main):
1. Run CI on main
2. Capture total coverage % from pytest output
3. If coverage >= 23% AND all tests green:
   - Create a new PR: `chore/raise-coverage-gate-23`
   - Update `pyproject.toml` `cov-fail-under=23`
   - Merge after approval
4. If coverage >= 25%:
   - Same process for `chore/raise-coverage-gate-25`

### Why This Approach?

- **No mid-workstream surprises**: Gates remain stable while PRs land
- **Atomic ratchet**: One clear commit per gate increase
- **Audit trail**: Each gate increase is a dedicated PR with justification
- **Risk mitigation**: If a PR introduces coverage regressions, they're caught at the gate increase step

---

## 4. Post-Integration Validation

Once all 5 integrity PRs have merged to main:

### Checklist

- [ ] All 5 PRs successfully merged (no reversions)
- [ ] Total test count: 359 (baseline) + 50 (integrity) = ~409 tests
- [ ] Coverage evaluation: Run `pytest --cov` on main
- [ ] Coverage ratchet decision: Is coverage >= 23%?
- [ ] If yes: Create and merge `chore/raise-coverage-gate-23`
- [ ] Docs review: Verify INTEGRITY_GUARANTEES.md is complete and accurate
- [ ] Known limitations: Verify KNOWN_LIMITATIONS.md covers all gaps

### Sign-Off

Once this checklist is complete and coverage gate raised:
- Update `docs/integrity/WORKSTREAM_PLAN.md` section 4 with completion date
- Flag as ready for next phase (e.g., `v0.1.7` release candidate)

---

## 5. Quick Reference: PR Landing Checklist

Use this table to track progress as each PR is submitted:

| PR # | Feature | Branch | Status | Tests | CI Green | Merged |
|------|---------|--------|--------|-------|----------|--------|
| 1 | Validation Threshold | `feature/integrity-validation-threshold` | 🔄 | 10 | ⏳ | ⏳ |
| 2 | Empty-Result Fail-Fast | `feature/integrity-empty-failfast` | 🔄 | 11 | ⏳ | ⏳ |
| 3 | Output Collision | `feature/integrity-export-collision` | 🔄 | 11 | ⏳ | ⏳ |
| 4 | Dedup Transparency | `feature/integrity-dedupe-transparency` | 🔄 | 10 | ⏳ | ⏳ |
| 5 | Timezone-Aware UTC | `feature/integrity-utc` | 🔄 | 8 | ⏳ | ⏳ |

**Legend**: 🟢 Done, 🔄 In Progress, ⏳ Pending, ❌ Blocked

---

## 6. References

- **Audit Report**: docs/integrity/AUDIT_REPORT.md
- **Guarantees**: docs/integrity/INTEGRITY_GUARANTEES.md
- **Known Limitations**: docs/integrity/KNOWN_LIMITATIONS.md
- **Safety Mode**: docs/integrity/MAXIMUM_SAFETY_MODE.md
- **Baseline**: docs/integrity/BASELINE.md

---

**Questions?** Contact the repo maintainer or create an issue tagged `integrity-workstream`.
