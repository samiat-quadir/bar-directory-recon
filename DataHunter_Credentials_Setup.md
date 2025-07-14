# Data Hunter Credentials Setup Template

Copy this to your actual config file after setting up credentials:

## Email Configuration (Gmail)

```json
"email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your-business-email@gmail.com",
    "password": "your-16-character-app-password",
    "to_emails": [
        "team@yourdomain.com",
        "alerts@yourdomain.com",
        "manager@yourdomain.com"
    ]
}
```

## Slack Configuration

```json
"slack": {
    "enabled": true,
    "webhook_url": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
}
```

## Environment Variables for Google Sheets

Add to your .env file:

```
SHEET_ID=1abcd1234efgh5678ijkl9012mnop3456qrst7890
GOOGLE_SHEETS_CREDENTIALS_PATH=config/google-sheets-service-account.json
```

## Quick Setup Steps

### 1. Gmail App Password

1. Go to <https://myaccount.google.com/security>
2. Enable 2-Factor Authentication
3. Go to "App passwords"
4. Generate new app password for "Data Hunter"
5. Use the 16-character password in config

### 2. Slack Webhook

1. Go to <https://api.slack.com/apps>
2. Create new app or use existing
3. Go to "Incoming Webhooks"
4. Create webhook for your channel
5. Copy webhook URL to config

### 3. Google Sheets Service Account

1. Go to <https://console.cloud.google.com/>
2. Create new project or use existing
3. Enable Google Sheets API
4. Create Service Account
5. Download JSON credentials
6. Share your Google Sheet with service account email

## Test Configuration

After setup, test with:

```bash
python test_data_hunter.py
python src/data_hunter.py --run-once
```
