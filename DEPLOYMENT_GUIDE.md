# 🚀 Production Deployment Checklist

## 🎯 Framework Status: ✅ READY FOR PRODUCTION

The unified scraping framework has been successfully productionized! Here's what you need to do to deploy it.

## 📋 Pre-Deployment Checklist

### 1. Verify Core Components

- [x] Unified scraping framework implemented
- [x] Legacy code archived
- [x] Schema unification complete
- [x] Notification system implemented
- [x] Security audit tools ready
- [x] Automation scripts updated

### 2. Missing Credentials/Configuration

#### Google Sheets Integration

If you plan to use Google Sheets export:

- [ ] Create Google Cloud Project
- [ ] Enable Google Sheets API
- [ ] Create credentials.json file
- [ ] Update config with sheet_id

#### Email Notifications

If you plan to use email notifications:

- [ ] Set environment variables:

  ```bash
  set EMAIL_ADDRESS=your-email@gmail.com
  set EMAIL_PASSWORD=your-app-password
  ```

#### SMS Notifications (Twilio)

If you plan to use SMS notifications:

- [ ] Set environment variables:

  ```bash
  set TWILIO_ACCOUNT_SID=your-account-sid
  set TWILIO_AUTH_TOKEN=your-auth-token
  set TWILIO_FROM_NUMBER=your-twilio-number
  ```

#### Slack Notifications

If you plan to use Slack notifications:

- [ ] Set environment variable:

  ```bash
  set SLACK_WEBHOOK_URL=your-webhook-url
  ```

## 🔧 Installation Steps

### 1. Install Required Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Google Sheets Dependencies (if needed)

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 3. Install Notification Dependencies (if needed)

```bash
pip install twilio requests
```

## 🧪 Testing

### 1. Test Core Framework

```bash
# Test schema functionality
python -c "from src.unified_schema import SchemaMapper; print('✅ Schema OK')"

# Test notification system
python -c "from src.notification_agent import NotificationAgent; print('✅ Notifications OK')"
```

### 2. Test Scraping and Export Formats

```bash
# Test lawyer directory (CSV export)
python unified_scraper.py scrape --config-dir config lawyer_directory --max-records 1 --verbose

# Test realtor directory (Excel export)
python unified_scraper.py scrape --config-dir config realtor_directory --max-records 1 --verbose

# Test with Google Sheets export (if configured)
python unified_scraper.py scrape --config-dir config lawyer_directory --max-records 5 --quiet
```

### 3. Test All Export Formats

```bash
# Verify CSV export
python -c "import pandas as pd; df = pd.read_csv('output/lawyer_directory/lawyer_directory_*.csv'); print(f'CSV: {len(df)} rows, {len(df.columns)} columns')"

# Verify Excel export
python -c "import pandas as pd; df = pd.read_excel('output/lawyer_directory/lawyer_directory_*.xlsx'); print(f'Excel: {len(df)} rows, {len(df.columns)} columns')"

# Verify JSON export
python -c "import json; data = json.load(open('output/lawyer_directory/lawyer_directory_*.json')); print(f'JSON: {len(data)} records')"

# Test schema consistency
python -c "from src.unified_schema import SchemaMapper; sm = SchemaMapper(); print('Schema Headers:', sm.get_export_headers('standard'))"
```

### 4. Test Notification System

```bash
# Test email notification (if configured)
python unified_scraper.py notify-test --type email

# Test SMS notification (if configured)
python unified_scraper.py notify-test --type sms

# Test Slack notification (if configured)
python unified_scraper.py notify-test --type slack

# Test all notifications at once
python unified_scraper.py notify-test --type all
```

## 📊 Configuration Examples

### Google Sheets Configuration

Update your config files (e.g., `config/lawyer_directory.json`):

```json
{
  "output": {
    "google_sheets": {
      "enabled": true,
      "sheet_id": "YOUR_GOOGLE_SHEET_ID",
      "worksheet_name": "Lawyers",
      "credentials_path": "credentials.json"
    }
  }
}
```

### Notification Configuration

Add to your config files (e.g., `config/lawyer_directory.json`):

```json
{
  "notifications": {
    "enabled": true,
    "triggers": {
      "on_completion": true,
      "on_error": true,
      "on_start": false
    },
    "email": {
      "enabled": true,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "use_tls": true,
      "sender_email": "${EMAIL_ADDRESS}",
      "sender_password": "${EMAIL_PASSWORD}",
      "sender_name": "Scraping Bot",
      "recipients": ["admin@example.com", "alerts@example.com"],
      "subject_template": "[SCRAPING] {status}: {config_name}",
      "include_stats": true,
      "include_sample_data": true
    },
    "sms": {
      "enabled": true,
      "twilio_account_sid": "${TWILIO_ACCOUNT_SID}",
      "twilio_auth_token": "${TWILIO_AUTH_TOKEN}",
      "from_number": "${TWILIO_FROM_NUMBER}",
      "to_numbers": ["+1234567890", "+1987654321"],
      "message_template": "Scraping {status}: {config_name}. Records: {record_count}",
      "include_error_details": true
    },
    "slack": {
      "enabled": true,
      "webhook_url": "${SLACK_WEBHOOK_URL}",
      "channel": "#scraping-alerts",
      "username": "Scraping Bot",
      "icon_emoji": ":robot_face:",
      "message_format": "rich",
      "include_attachments": true,
      "mention_on_error": ["@channel"]
    }
  }
}
```

## 🔄 Scheduled Automation

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., weekly)
4. Set action: Start a program
5. Program: `powershell.exe`
6. Arguments: `-ExecutionPolicy Bypass -File "C:\Code\bar-directory-recon\weekly_automation.ps1"`

### Manual Execution

```bash
# Weekly automation (PowerShell)
powershell -ExecutionPolicy Bypass -File weekly_automation.ps1

# Google Sheets export (PowerShell)
powershell -ExecutionPolicy Bypass -File Automated-GoogleSheets-Export.ps1
```

## 🛠️ Production Commands

### Standard Scraping

```bash
# Quiet mode (for scheduled runs)
python unified_scraper.py scrape --config-dir config lawyer_directory --quiet

# Verbose mode (for debugging)
python unified_scraper.py scrape --config-dir config realtor_directory --verbose
```

### Batch Processing

```bash
# Process all configured directories
python unified_scraper.py scrape --config-dir config lawyer_directory --quiet
python unified_scraper.py scrape --config-dir config realtor_directory --quiet
```

### Security Auditing

```bash
# Audit configuration security
python unified_scraper.py audit-security --config-dir config
```

## 🔍 Troubleshooting

### Common Issues

**1. Google Sheets Authentication**

- Ensure credentials.json is in the correct location
- Check Google Cloud Console for API limits
- Verify sheet_id is correct

**2. Email Notifications**

- Use app passwords for Gmail
- Check SMTP settings and ports
- Verify firewall settings

**3. SMS Notifications**

- Verify Twilio account is active
- Check phone number format (+1234567890)
- Confirm account has credits

**4. Import Errors**

- Ensure all dependencies are installed
- Check Python version compatibility
- Verify virtual environment activation

## 📈 Monitoring

### Log Files

- Check `logs/` directory for execution logs
- Monitor `output/` directory for exported data
- Review automation script logs

### Health Checks

- Regular notification tests
- Schema validation checks
- Configuration audits

## 🎉 You're Ready

The framework is now production-ready with:

- ✅ Unified data schema
- ✅ Secure credential management
- ✅ Comprehensive notification system
- ✅ Automated scheduling
- ✅ Legacy code archived
- ✅ Production-ready CLI

**Next Steps:**

1. Configure your credentials
2. Test the system
3. Schedule your automations
4. Monitor and maintain

---

**Need Help?**

- Check the logs in `logs/` directory
- Review configuration files in `config/`
- Use `--verbose` flag for detailed output
- Test individual components first
