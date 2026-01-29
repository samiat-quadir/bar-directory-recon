# Pricing and Scope

**Note:** This is a reference guide for **setup, first export, and refresh tiers**. Consult your service agreement for specific commercial terms.

---

## What's Included in Bar Directory Recon

### Core Functionality (All Plans)

- **CSV-to-Google Sheets Export**
  - Single-run exports
  - Append, replace, or update-only modes
  - Deduplication by key column
  - Error logging and reporting
  - Health checks via `bdr doctor`

- **Installation & Setup**
  - Python package installation via pip
  - Service Account JSON setup (Google Cloud)
  - Environment variable configuration
  - Dry-run validation before live export

- **Documentation & Onboarding**
  - Public docs (START_HERE.md, how-to guides)
  - CLIENT_ONBOARDING_CHECKLIST.md
  - Troubleshooting guides
  - Template Google Sheet specifications

---

## Setup Phase (Initial Onboarding)

This is the one-time effort to get BDR running in your environment.

### Scope

1. **Environment Setup** (your responsibility)
   - Install Python 3.11+ on your machine/server
   - Create a Google Cloud project and Service Account
   - Download Service Account JSON key
   - Share target Google Sheet with Service Account email
   - Set `GOOGLE_SHEETS_CREDENTIALS_PATH` and `GOOGLE_SHEETS_SPREADSHEET_ID` environment variables

2. **Tool Installation** (automated via pip)
   - `pip install "bar-directory-recon[gsheets]"`
   - Verify health: `bdr doctor --no-exec`

3. **First Test Export** (manual, 10–30 minutes)
   - Prepare a small test CSV (5–10 rows)
   - Run dry-run: `bdr export csv-to-sheets test.csv --sheet-id <ID> --dry-run`
   - Run live export: `bdr export csv-to-sheets test.csv --sheet-id <ID>`
   - Verify rows in Google Sheet

### Typical Timeline

- **Self-serve:** 30–60 minutes (if you're comfortable with CLI, APIs, and Cloud Console)
- **With support:** 1–2 hours (guided via docs or email)

### Support Tier

**Standard:** Email support via intake template (SUPPORT_INTAKE_TEMPLATE.md)  
**Premium:** DM/Slack for same-day response (if subscribed)

---

## First Export Phase

The first export is your "production run"—export real attorney lead data.

### Scope

1. **Data Preparation**
   - Export your source list from your system (e.g., data warehouse, CRM)
   - Clean/validate CSV format
   - Test with `bdr doctor` and `--dry-run`

2. **Sheet Preparation**
   - Ensure Google Sheet has correct headers (matching CSV)
   - Verify sheet is shared with Service Account email
   - Choose export mode: **append** (safe, default), **replace** (clears sheet first), or **update-only** (upserts by key)

3. **Export Execution** (typically 2–10 minutes for 500–5,000 rows)
   ```bash
   bdr export csv-to-sheets data.csv \
     --sheet-id <ID> \
     --worksheet leads \
     --mode append
   ```

4. **Validation**
   - Count rows in Google Sheet (should match CSV + existing rows if append mode)
   - Spot-check 5–10 rows for correct data
   - Review any error logs if used `--log-errors`

### Typical Timeline

- **Data prep:** 15–30 minutes
- **Export execution:** 2–10 minutes (depending on row count)
- **Validation:** 5–10 minutes
- **Total:** 30–50 minutes for first run

---

## Refresh Phase (Recurring)

After the first export, subsequent runs can be automated or scheduled.

### Scope: **Tier 1 — Manual Refresh** (No Extra Cost)

- **Frequency:** As-needed, on-demand
- **Process:**
  1. Export fresh data to CSV
  2. Run: `bdr export csv-to-sheets fresh.csv --sheet-id <ID>`
  3. Verify results in Google Sheet
- **Effort:** 5–10 minutes per run
- **Ideal for:** Weekly or bi-weekly exports, small data sets

---

### Scope: **Tier 2 — Basic Automation** (If Desired)

Configure a scheduled task (no code changes needed):

**Windows (Task Scheduler):**
- Use wrapper script: `scripts/run_export.ps1`
- Schedule via Task Scheduler with 30-minute retry on failure
- Logs saved to `logs/exports/<timestamp>.log`

**macOS/Linux (Cron):**
- Use wrapper script: `scripts/run_export.sh`
- Add cron entry: `0 8 * * 1 /path/to/run_export.sh`
- Logs saved to `logs/exports/<timestamp>.log`

**Effort:** 30–60 minutes one-time setup  
**Recurring effort:** 0 (fully automated)

---

### Scope: **Tier 3 — Scheduled with Error Handling** (If Subscribed)

Coming in **v0.2.0+**:
- Automatic retry on transient failures
- Email alerts on export failure
- Batch processing (multiple CSVs in one run)
- Update-only mode with change detection
- Admin dashboard (export history, audit log)

**Estimated added effort:** 0 (set-and-forget)

---

## Common Scenarios & Time Estimates

| Scenario | Effort | Tool Used |
|----------|--------|-----------|
| One-time export of 1,000 attorney records | 45 min | Manual run + validation |
| Weekly export, same data source | 10 min/week | Scheduled wrapper script |
| Monthly export, 5 different CSVs | 30 min/month | Multiple manual runs or batch mode (v0.2.0+) |
| Export with deduplication by email | 60 min first run, 10 min refresh | `--dedupe-key email` flag |
| Multi-sheet export (leads + firms) | 60 min first run | Multiple sheet IDs, run twice |

---

## What's NOT Included (Out of Scope)

- **Data transformation** (you provide clean CSV; BDR imports as-is)
- **Row deduplication logic** (BDR deduplicates by key; you define the key)
- **Google Sheets formula creation** (You create formulas if desired post-import)
- **CRM/database integration** (You export CSV from your system manually or via your CRM's API)
- **Bulk data validation** (You validate CSV before import)
- **Compliance/GDPR handling** (You ensure data handling meets your org's policies)

**For these, consult:**
- Your CRM or data system's API docs
- Google Sheets formula library
- Your legal/compliance team

---

## Pricing Summary

| Phase | Cost | Includes |
|-------|------|----------|
| **Installation (open source)** | Free | pip install, docs, support via GitHub issues |
| **First Export** | Free | 1 guided setup + first export |
| **Refreshes (Tier 1 – manual)** | Free | Unlimited on-demand exports + wrapper scripts |
| **Automat. (Tier 2 – scheduled)** | Included | Wrapper scripts for Windows/Linux/macOS |
| **Premium Support** | Contact sales | DM/Slack support, SLA, custom development |
| **Tier 3 (v0.2.0+)** | TBD | Batch, retry, email alerts, dashboard |

---

## Getting Started

1. **Review CLIENT_ONBOARDING_CHECKLIST.md** for step-by-step setup
2. **Prepare your first CSV** (5–10 test rows)
3. **Create and share a Google Sheet** (see TEMPLATE_SHEET_SPEC.md)
4. **Run `bdr doctor --no-exec`** to check environment
5. **Run `bdr export csv-to-sheets --help`** for all options
6. **Test with `--dry-run`** before going live
7. **Export and validate** your first real batch
8. **Auto-schedule via Tier 2** if recurring (optional)

---

## Questions & Support

Refer to:
- **SUPPORT_INTAKE_TEMPLATE.md** — Submit structured issue reports
- **TROUBLESHOOTING_ONE_PAGE.md** — Fix 5 common problems
- **GitHub Issues** — Public bug reports and feature requests
- **Email support** — Non-urgent questions or onboarding help

---

**Thank you for using Bar Directory Recon!**
