# Google Sheets Integration Setup

This guide walks you through setting up Google Sheets API access for `bar-directory-recon`.

## Prerequisites

- A Google Cloud project (free tier is sufficient)
- A Google account
- The `bar-directory-recon` package installed with Google Sheets support
- A Google Sheet you want to use for data export

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top left
3. Click **NEW PROJECT**
4. Enter a project name (e.g., "bar-directory-recon")
5. Click **CREATE**
6. Wait for the project to be created, then select it

## Step 2: Enable Google Sheets API

1. In the Cloud Console, click **Go to APIs overview** (or search for "API")
2. Click **ENABLE APIS AND SERVICES**
3. Search for **"Google Sheets API"**
4. Click the result
5. Click **ENABLE**
6. Wait for it to finish enabling

## Step 3: Create a Service Account

1. In the Cloud Console, click **Create Credentials** (or go to Credentials in the left menu)
2. Select **Service Account** from the dropdown
3. Enter a service account name (e.g., "bar-directory-recon-export")
4. Click **CREATE AND CONTINUE**
5. (Grant roles step) Click **CONTINUE** (you'll set permissions later)
6. (Create keys step) Click **CONTINUE**
7. You should now be on the Service Accounts list page

## Step 4: Generate and Download the Key

1. Find your service account in the list and click on it
2. Go to the **KEYS** tab
3. Click **ADD KEY** → **Create new key**
4. Select **JSON**
5. Click **CREATE**
6. The JSON key file will download automatically
7. **Save this file securely** — it contains your credentials
   - Suggested location:
     - **Linux/macOS**: `~/.config/gcp-key.json`
     - **Windows**: `%USERPROFILE%\.config\gcp-key.json` or `C:\Users\<YourName>\.config\gcp-key.json`
8. **IMPORTANT**: Never commit this file to Git. Add it to `.gitignore` if storing in a local project folder.

## Step 5: Share Your Google Sheet

1. Open your Google Sheet
2. Click **Share** (top right)
3. In the "Share with people and groups" field, paste the service account email
   - You can find this email in the JSON key file (look for `"client_email": "..."`)
   - Or find it in the Cloud Console under Service Accounts
4. Give it **Editor** permissions (so it can write data)
5. Click **Share**
6. If prompted about external sharing, click **Share anyway**

## Step 6: Set the Environment Variable

Once you have the JSON key file, set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to it.

### Linux / macOS (Bash/Zsh)

```bash
export GOOGLE_APPLICATION_CREDENTIALS=~/.config/gcp-key.json
```

Add this line to your `~/.bashrc` or `~/.zshrc` to make it persistent:

```bash
echo 'export GOOGLE_APPLICATION_CREDENTIALS=~/.config/gcp-key.json' >> ~/.bashrc
source ~/.bashrc
```

### Windows (PowerShell)

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\Users\YourName\.config\gcp-key.json"
```

To make it persistent, add it to your PowerShell profile or use the System Environment Variables panel:

1. Press `Win + R`, type `sysdm.cpl`, and press Enter
2. Go to **Advanced** → **Environment Variables**
3. Click **New** (under User variables)
4. Variable name: `GOOGLE_APPLICATION_CREDENTIALS`
5. Variable value: `C:\Users\YourName\.config\gcp-key.json`
6. Click **OK**

### Windows (Command Prompt)

```cmd
set GOOGLE_APPLICATION_CREDENTIALS=C:\Users\YourName\.config\gcp-key.json
```

## Step 7: Verify Setup

Run the health check:

```bash
bdr doctor
```

You should see:

```
Overall: PASS
  Google Sheets API: OK
  Credentials loaded: YES
  Sheets can be accessed: YES
```

## Troubleshooting

### "Permission denied" or "403 Forbidden"

- Make sure you shared the Google Sheet with the service account email (Step 5)
- Check that you gave it **Editor** permissions

### "Credentials not found" or "Invalid key"

- Verify `GOOGLE_APPLICATION_CREDENTIALS` is set correctly
- Make sure the JSON key file exists and hasn't been moved
- Try running `echo $GOOGLE_APPLICATION_CREDENTIALS` (Linux/macOS) or `$env:GOOGLE_APPLICATION_CREDENTIALS` (PowerShell) to confirm

### "Authentication to Google API failed"

- Delete the local credential file and regenerate a new key (Step 4)
- Make sure you enabled the **Google Sheets API** (Step 2)

## Security Reminder

✅ **DO**: Store the JSON key securely (home directory, not in Git)
✅ **DO**: Use one key per service (don't reuse keys)
✅ **DO**: Rotate keys periodically

❌ **DON'T**: Commit the JSON key to Git
❌ **DON'T**: Share the JSON key via email or chat
❌ **DON'T**: Use the key in public code repositories

## Next Steps

Now that Google Sheets is configured, see:

- [CSV to Sheets Usage](../usage/csv-to-sheets.md) — detailed examples of exporting data
- [Troubleshooting](../troubleshooting.md) — solutions to common issues
