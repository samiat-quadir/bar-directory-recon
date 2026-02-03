# Pilot Client Intake Form

**Standard Intake for Bar Directory Recon Pilot Program**

**Last Updated**: 2026-02-03  
**Version**: v0.1.13

---

## What is This?

This form captures essential information **before** a client runs their first export. It ensures:
- All prerequisites are met before we begin
- Support can respond quickly if issues arise
- Success criteria are clear and measurable
- Setup mirrors the [PILOT_RUN_SOP.md](PILOT_RUN_SOP.md)

---

## Client Information

| Field | Response |
|-------|----------|
| **Client Name** | [Your organization] |
| **Primary Contact** | [Name & email] |
| **Secondary Contact** | [Name & email] (optional) |
| **Timezone** | [e.g., EST, PST, UTC] |

---

## Data Requirements

| Requirement | Status | Details |
|-------------|--------|---------|
| **CSV File Ready** | ☐ Yes ☐ No | [File name, row count, column count] |
| **CSV Has Headers** | ☐ Yes ☐ No | First row contains column names |
| **Column List** | ☐ Ready | [Paste header row or column list] |
| **Sample Rows (2–3)** | ☐ Attached | [Sanitize any sensitive data] |
| **File Size** | ☐ < 10 MB | [Approximate row count for reference] |

---

## Google Sheets Setup

| Item | Status | Details |
|------|--------|---------|
| **Google Sheet Created** | ☐ Yes ☐ No | [Google Sheets URL] |
| **Sheet ID Extracted** | ☐ Yes ☐ No | [Sheet ID from URL: docs.google.com/spreadsheets/d/{ID}/edit] |
| **Service Account Created** | ☐ Yes ☐ No | [Service account email, e.g., sa@project.iam.gserviceaccount.com] |
| **Service Account JSON** | ☐ Downloaded | [Saved outside the repository] |
| **Sheet Shared w/ SA** | ☐ Yes ☐ No | [Service account has Editor access] |

---

## Integration Preferences

### Deduplication Key

```
Column name (if needed to avoid duplicates on re-run):  [e.g., "id", "location_key", or "none"]
```

### Export Mode (Pilot Recommendation: **Append**)

| Mode | Description | Risk | Recommendation |
|------|-------------|------|-----------------|
| **append** | New rows added; no overwrites | Low | ✅ **Start here** |
| **replace** | Sheet cleared and reloaded | High | ⚠️ Only after validation |
| **safe-mode** | Dry-run; no write; preview only | None | ✅ **Run first before append** |

**Selected Mode**: ☐ append ☐ replace ☐ safe-mode first, then append

### Refresh Cadence

How often will data be exported?

- ☐ **Ad-hoc** (manual, as needed)
- ☐ **Daily** (same time each day; e.g., 6 AM EST)
- ☐ **Weekly** (day + time; e.g., Monday 2 PM EST)
- ☐ **Monthly** (if applicable)

**Details**: [Frequency and time window]

---

## Environment Prerequisites

### Python & Installation

| Check | Status | Details |
|-------|--------|---------|
| **Python 3.11+** | ☐ Verified | `python --version` output: [e.g., Python 3.11.8] |
| **pip Accessible** | ☐ Verified | `pip --version` output: [e.g., pip 24.0] |
| **Wheel Installed** | ☐ Verified | `bdr --version` output: [e.g., 0.1.13] |

### Credentials

| Check | Status | Confirmation |
|-------|--------|-------------|
| **Credentials JSON Saved** | ☐ Yes | [Location: /path/to/sa-key.json—NOT in repo] |
| **Env Var Set** | ☐ Yes | [Confirm: `echo $GOOGLE_SHEETS_CREDENTIALS_PATH` or PowerShell equivalent] |

---

## Success Criteria

Check off when complete:

- [ ] **Installation validated**: `bdr doctor --no-exec` returns `Overall: PASS`
- [ ] **Credentials verified**: No auth errors in `doctor` output
- [ ] **Dry-run succeeded**: `bdr export csv-to-sheets ... --safe-mode` completes with data preview
- [ ] **Production export succeeded**: `bdr export csv-to-sheets ... --mode append` completes
- [ ] **Google Sheets verified**: Expected rows appear in target Sheet
- [ ] **Row count correct**: Within expected range (original CSV row count ± dedup variance)
- [ ] **No encoding artifacts**: Text displays correctly (no garbled UTF-8)
- [ ] **Timestamps correct**: Data reflects expected dates/times
- [ ] **Contact provided**: Customer can give feedback or report issues

---

## Pilot Phase Timeline

| Phase | Duration | Checkpoint |
|-------|----------|-----------|
| **Pre-Integration** | 1–2 hours | Intake form completed |
| **Install & Verify** | 30–60 min | `bdr doctor` passes; env var set |
| **Dry-Run** | 10 min | `--safe-mode` preview reviewed |
| **First Export** | 5 min | Data in Google Sheets; row count validated |
| **Iteration** (if needed) | Variable | Troubleshoot via [Support Packet](SUPPORT_PACKET.md) |
| **Sign-Off** | 10 min | Client confirms success |

**Target Duration**: 2–3 hours (end-to-end, including troubleshooting)

---

## Support & Escalation

### If Issues Arise

1. **Check docs**: [PILOT_RUN_SOP.md](PILOT_RUN_SOP.md) troubleshooting table
2. **Gather support packet**: See [SUPPORT_PACKET.md](SUPPORT_PACKET.md)
3. **Report**: Share support packet via email or GitHub issue

### Contact Points

- **Documentation**: [docs/ops/PILOT_RUN_SOP.md](PILOT_RUN_SOP.md)
- **Support Packet Template**: [docs/ops/SUPPORT_PACKET.md](SUPPORT_PACKET.md)
- **Repository**: [github.com/samiat-quadir/bar-directory-recon](https://github.com/samiat-quadir/bar-directory-recon)
- **Issues**: Open [GitHub Issue](https://github.com/samiat-quadir/bar-directory-recon/issues) with support packet attached

---

## Pilot Sign-Off

Complete when integration is successful:

```
✅ Pilot Integration Complete

Client: [Name]
Date: [YYYY-MM-DD]
Version: v0.1.13
CSV Rows: [Count]
Sheet ID: [Redacted—recorded separately]
Mode Used: [append/replace/safe-mode]
Next Steps: [ad-hoc / daily / weekly / other schedule]

Issues Encountered: [None / list here]
Time to Complete: [Total duration]
```

---

## Next Steps

After successful pilot validation:

1. **Schedule refresh** (if applicable): Set up cron / Task Scheduler
2. **Monitor first run**: Check logs and Google Sheets for expected updates
3. **Iterate**: Expand to additional CSV files or sheets
4. **Feedback**: Share what worked, what didn't
5. **Scale**: Move to production if all checks pass

---

## Notes for Support Team

- **Escalation criteria**: If `bdr doctor` fails OR any auth error occurs, escalate immediately
- **Common issues**: See PILOT_RUN_SOP.md troubleshooting table
- **Success rate target**: 95%+ pilots pass validation without escalation
- **Follow-up**: Check in 1 week post-validation for feedback
