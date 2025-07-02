# Google Sheets API Setup Guide - Phase 4 Optimize Prime

## Overview

Phase 4 of the Universal Lead Generation System includes advanced Google Sheets integration for real-time lead management, batch upserts, deduplication, and automated formatting.

## Features

- **Batch Upsert**: Efficiently insert/update multiple leads at once
- **Automatic Deduplication**: Avoid duplicate leads based on email/phone
- **Rate Limiting**: Respectful API usage with built-in delays
- **Error Handling**: Graceful handling of API limits and network issues
- **Conditional Formatting**: Automatic highlighting of urgent leads
- **Tag Management**: Industry and location-based lead tagging

## Prerequisites

### 1. Install Required Dependencies

```bash
pip install google-api-python-client google-auth pandas openpyxl
```

### 2. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Sheets API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"

### 3. Create Service Account

1. Navigate to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the service account details:
   - **Name**: `lead-generation-service`
   - **Description**: `Service account for Universal Lead Generation System`
4. Click "Create and Continue"
5. Skip role assignment (click "Continue")
6. Click "Done"

### 4. Generate Service Account Key

1. Click on the created service account
2. Navigate to "Keys" tab
3. Click "Add Key" > "Create New Key"
4. Select "JSON" format
5. Click "Create"
6. Save the downloaded JSON file as `config/google_service_account.json` in your project directory

### 5. Share Google Sheet with Service Account

1. Open your Google Sheet
2. Click "Share" button
3. Add the service account email (found in the JSON file under `client_email`)
4. Give "Editor" permissions
5. Uncheck "Notify people" and click "Share"

## Configuration

### Directory Structure

```
bar-directory-recon/
├── config/
│   └── google_service_account.json    # Service account credentials
├── lead_enrichment_plugin.py          # Lead enrichment engine
├── google_sheets_integration.py       # Sheets integration
├── universal_automation.py            # Main automation script
└── notify_agent.py                    # Urgent lead notifications
```

### Environment Variables (Optional)

You can also configure using environment variables:

```bash
# Google Sheets Configuration
export GOOGLE_SERVICE_ACCOUNT_PATH="config/google_service_account.json"
export DEFAULT_GOOGLE_SHEET_ID="1ABC...xyz"
export DEFAULT_GOOGLE_SHEET_NAME="Leads"

# Notification Configuration (for urgent leads)
export EMAIL_USERNAME="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"
export TO_EMAILS="recipient1@example.com,recipient2@example.com"
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
```

## Usage Examples

### Basic Google Sheets Integration

```python
from google_sheets_integration import export_leads_to_sheets

# Sample leads data
leads = [
    {
        "name": "John Smith",
        "company": "Smith Pool Services", 
        "email": "john@smithpools.com",
        "phone": "(555) 123-4567",
        "industry": "pool_contractors",
        "city": "Miami",
        "state": "FL",
        "lead_score": 85,
        "urgency_flag": True
    }
]

# Export to Google Sheets
success, stats = export_leads_to_sheets(
    leads=leads,
    sheet_id="1ABC...xyz",  # Your Google Sheet ID
    sheet_name="Pool Contractors",
    avoid_duplicates=True
)

print(f"Export successful: {success}")
print(f"Stats: {stats}")
```

### CLI Usage with Google Sheets

```bash
# Single industry with Google Sheets export
python universal_automation.py --industry pool_contractors --city Miami --state FL --google-sheet-id 1ABC...xyz

# Interactive mode (will prompt for sheet details)
python universal_automation.py --interactive

# All industries with sheets integration
python universal_automation.py --industry all --city Tampa --state FL --google-sheet-id 1ABC...xyz --max-records 100
```

### Advanced Integration Example

```python
from universal_automation import UniversalLeadAutomation
from google_sheets_integration import GoogleSheetsIntegration

# Initialize automation
automation = UniversalLeadAutomation()

# Run with enrichment and sheets integration
result = automation.scrape_industry(
    industry="lawyers",
    city="Orlando", 
    state="FL",
    max_records=50,
    test_mode=False,
    google_sheet_id="1ABC...xyz",
    google_sheet_name="Orlando_Lawyers",
    enable_enrichment=True
)

# Check results
if result["success"]:
    print(f"Found {result['count']} leads")
    print(f"Enriched {result['enriched_count']} leads")
    print(f"Google Sheets uploaded: {result['google_sheets_uploaded']}")
    print(f"Urgent leads: {result['urgent_leads']}")
```

## Google Sheet Setup

### 1. Create New Spreadsheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Name it (e.g., "Universal Lead Generation - Phase 4")
4. Copy the Sheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/1ABC...xyz/edit
                                          ^^^^^^^^^^^
                                          This is your Sheet ID
   ```

### 2. Recommended Sheet Structure

The system will automatically create headers, but you can pre-format:

| Column | Field | Description |
|--------|-------|-------------|
| A | name | Contact name |
| B | company | Business name |
| C | email | Email address |
| D | phone | Phone number |
| E | address | Street address |
| F | city | City |
| G | state | State |
| H | zip_code | ZIP code |
| I | website | Website URL |
| J | industry | Industry category |
| K | business_type | Business type |
| L | description | Business description |
| M | source | Data source |
| N | linkedin_url | LinkedIn profile |
| O | facebook_url | Facebook page |
| P | twitter_url | Twitter profile |
| Q | instagram_url | Instagram profile |
| R | reviews_count | Number of reviews |
| S | average_rating | Average rating |
| T | lead_score | Lead score (0-100) |
| U | urgency_flag | Urgent lead flag |
| V | urgency_reason | Urgency reason |
| W | email_verified | Email verification status |
| X | phone_verified | Phone verification status |
| Y | created_date | Creation timestamp |
| Z | last_updated | Last update timestamp |

### 3. Conditional Formatting for Urgent Leads

The system automatically applies conditional formatting:

- **Red background**: Urgent leads (urgency_flag = TRUE)
- **Bold text**: High-score leads (lead_score >= 80)
- **Green border**: Verified contacts (email_verified = TRUE)

## Troubleshooting

### Common Issues

#### 1. Permission Denied
```
Error: The caller does not have permission
```
**Solution**: Ensure the service account email is added to your Google Sheet with Editor permissions.

#### 2. API Not Enabled
```
Error: Google Sheets API has not been used in project
```
**Solution**: Enable Google Sheets API in Google Cloud Console.

#### 3. Quota Exceeded
```
Error: Quota exceeded for quota metric
```
**Solution**: The system includes automatic rate limiting. Wait a few minutes and try again.

#### 4. Invalid Credentials
```
Error: Could not automatically determine credentials
```
**Solution**: Check that `config/google_service_account.json` exists and is valid.

### Debug Mode

Enable verbose logging to troubleshoot issues:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)

# Run your automation with debug logging
```

### Validation Script

Test your setup:

```python
from google_sheets_integration import GoogleSheetsIntegration

# Test connection
integration = GoogleSheetsIntegration()
if integration.connect():
    print("✅ Google Sheets connection successful!")
    
    # Test with sample data
    test_leads = [{
        "name": "Test Lead",
        "email": "test@example.com", 
        "company": "Test Company",
        "industry": "test",
        "lead_score": 50
    }]
    
    success, stats = integration.export_leads(
        test_leads, 
        "1ABC...xyz",  # Your sheet ID
        "Test Sheet"
    )
    
    print(f"Test export: {success}")
    print(f"Stats: {stats}")
else:
    print("❌ Connection failed - check credentials and permissions")
```

## Security Best Practices

### 1. Protect Service Account Key
- Never commit `google_service_account.json` to version control
- Add to `.gitignore`:
  ```
  config/google_service_account.json
  config/*.json
  ```

### 2. Limit Service Account Permissions
- Only share sheets that need automation
- Use separate service accounts for different projects
- Regularly rotate service account keys

### 3. Environment Variables
- Store sensitive data in environment variables
- Use `.env` files for local development
- Never hardcode credentials in source code

## Performance Optimization

### 1. Batch Operations
The system automatically batches operations for efficiency:
- Default batch size: 100 rows
- Configurable via `batch_size` parameter
- Automatic retry with exponential backoff

### 2. Rate Limiting
Built-in rate limiting prevents API quota issues:
- 1 second delay between requests
- Automatic quota monitoring
- Graceful degradation on limits

### 3. Caching
- Local caching of sheet metadata
- Duplicate detection optimization
- Minimal API calls for status checks

## API Limits and Quotas

### Google Sheets API Limits
- **Read requests**: 300 per minute per project
- **Write requests**: 300 per minute per project
- **Requests per 100 seconds per user**: 100

### Best Practices
- Use batch operations when possible
- Implement exponential backoff
- Cache data locally when appropriate
- Monitor quota usage in Google Cloud Console

## Support and Updates

### Getting Help
1. Check this documentation first
2. Review error logs for specific issues
3. Test with minimal examples
4. Check Google Cloud Console for API status

### Updates
Phase 4 includes automatic error handling and self-healing capabilities. The system will:
- Automatically retry failed operations
- Fall back to CSV export if Sheets unavailable
- Log all operations for debugging
- Provide detailed error messages

---

*Generated by Universal Lead Generation System - Phase 4 Optimize Prime*
*Last Updated: July 2, 2025*
