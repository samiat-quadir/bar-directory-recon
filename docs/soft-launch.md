# Soft Launch Quickstart

Welcome to **Bar Directory Recon (BDR)** — a tool for extracting and organizing legal professional data from bar directories.

---

## What is BDR?

Bar Directory Recon automates the discovery and extraction of attorney information from state bar association websites and other legal directories. It exports structured data directly to Google Sheets for easy review, outreach, and follow-up.

### Who is this for?

- **Legal recruiters** seeking attorney leads
- **Law firm marketing teams** building outreach lists
- **Legal tech companies** analyzing market data
- **Solo practitioners** researching competitors or potential referral partners

---

## Quick Setup (5 minutes)

### Prerequisites

- Python 3.11+
- A Google Cloud service account with Sheets API access
- A Google Spreadsheet shared with your service account

### Step 1: Install Dependencies

```bash
# Clone and install
git clone https://github.com/samiat-quadir/bar-directory-recon.git
cd bar-directory-recon
pip install -e .[gsheets]
```

### Step 2: Create Your Google Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or use an existing one)
3. Enable the **Google Sheets API**
4. Create a **Service Account** and download the JSON key file
5. Save it securely (e.g., `C:\secrets\bdr-service-account.json`)

### Step 3: Share Your Spreadsheet

1. Create a new Google Spreadsheet
2. Share it with your service account email (e.g., `bdr@your-project.iam.gserviceaccount.com`)
3. Give it **Editor** access
4. Copy the Spreadsheet ID from the URL:

   ```text
   https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit
   ```

### Step 4: Create `.env.local`

Create a file named `.env.local` in the repository root:

```bash
GOOGLE_SHEETS_CREDENTIALS_PATH=C:\secrets\bdr-service-account.json
GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id-here
```

> ⚠️ **Security**: `.env.local` is gitignored and will not be committed.

---

## One-Command Demo

Run the demo to verify everything works:

```powershell
.\scripts\gsheets-demo.ps1
```

This will:

1. Activate the virtual environment
2. Load your `.env.local` credentials
3. Check that dependencies are installed
4. List available worksheets
5. Export a demo row to the "leads" worksheet

### Options

```powershell
# Target a different worksheet
.\scripts\gsheets-demo.ps1 -Worksheet "Sheet1"

# Dry-run mode (no network calls)
.\scripts\gsheets-demo.ps1 -DryRun
```

---

## Troubleshooting

### "Worksheet 'leads' not found"

The default worksheet is "leads". If your spreadsheet doesn't have this worksheet:

```powershell
# List available worksheets
python -m tools.gsheets_exporter --list-worksheets

# Use a different worksheet
.\scripts\gsheets-demo.ps1 -Worksheet "Sheet1"
```

### "GOOGLE_SHEETS_CREDENTIALS_PATH not set"

Make sure `.env.local` exists in the repository root with the correct path:

```bash
GOOGLE_SHEETS_CREDENTIALS_PATH=C:\path\to\your\service-account.json
```

### "Credentials file not found"

Double-check the path in your `.env.local`. Use the full absolute path.

### "Google Sheets dependencies NOT installed"

Install the gsheets extra:

```bash
pip install .[gsheets]
```

### "Permission denied" on the spreadsheet

Make sure you've shared the spreadsheet with your service account email address.

---

## Offer v1 — Pricing

### 🚀 Setup + First Export (One-Time)

**$XXX** — Includes:

- Google Sheets integration setup
- Service account configuration assistance
- First successful export verification
- 30-minute onboarding call

### 📅 Monthly Refresh Subscription

**$XX/month** — Includes:

- Scheduled data refreshes (weekly or monthly)
- Automatic export to your Google Sheet
- Basic email support
- Up to X directories monitored

### ✨ Verification & Enrichment Add-On (Future)

**Coming Soon** — Additional features:

- Email verification (reduce bounce rates)
- LinkedIn profile matching
- Firm size and practice area enrichment
- Custom data fields

---

## Next Steps

1. Complete the [Quick Setup](#quick-setup-5-minutes)
2. Run the [One-Command Demo](#one-command-demo)
3. [Contact us](mailto:your-email@example.com) to discuss Offer v1

---

## Documentation

- [Full Integration Guide](integrations.md)
- [CLI Reference](../README.md#quick-demo)
- [Troubleshooting](integrations.md#security-guidance)

---

Last updated: January 2026
