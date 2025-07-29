# 🏠 Realtor Directory Automation

Automated lead scraping system for <https://directories.apps.realtor/?type=member>

## 🎯 Features

- **Automated Lead Extraction**: Scrapes name, email, phone, business name, and address
- **Multiple Output Formats**: CSV files and optional Google Sheets integration
- **Flexible Scheduling**: Weekly automation with Windows Task Scheduler
- **Interactive Mode**: Custom search parameters and real-time configuration
- **Cross-Device Compatible**: Works on Windows, macOS, and Linux
- **Comprehensive Logging**: Detailed execution logs and error tracking

## 🚀 Quick Start

### 1. Setup Installation

Run the setup script to install dependencies and configure the system:

```bash
python setup_realtor_automation.py
```

This will:

- Create a virtual environment
- Install all required dependencies
- Create necessary directories (outputs/, logs/, config/)
- Generate configuration templates
- Create Windows Task Scheduler integration files

### 2. Basic Usage

#### Windows (Recommended)

```cmd
RunRealtorAutomation.bat
```

#### Command Line

```bash
# Single scrape with default settings
python realtor_automation.py --mode once

# Interactive mode with custom parameters
python realtor_automation.py --mode interactive

# Start weekly scheduler
python realtor_automation.py --mode schedule
```

#### Python Integration

```python
from universal_recon.plugins.realtor_directory_plugin import scrape_realtor_directory

# Basic usage
result = scrape_realtor_directory(
    output_path="my_leads.csv",
    max_records=100,
    verbose=True
)

# With search parameters
result = scrape_realtor_directory(
    output_path="california_agents.csv",
    search_params={"state": "CA", "city": "Los Angeles"},
    google_sheet_id="your_sheet_id_here",
    verbose=True
)
```

## 📋 CLI Reference

### Main Script Arguments

```bash
python realtor_automation.py [OPTIONS]
```

| Option | Description | Example |
|--------|-------------|---------|
| `--mode` | Execution mode: `once`, `interactive`, `schedule` | `--mode once` |
| `--max-records` | Maximum number of records to scrape | `--max-records 500` |
| `--output` | Custom output file path | `--output "my_leads.csv"` |
| `--google-sheet-id` | Google Sheets ID for upload | `--google-sheet-id "1BxiMVs0..."` |

### Universal Recon Integration

```bash
python universal_recon/main.py --site realtor_directory [OPTIONS]
```

| Option | Description | Example |
|--------|-------------|---------|
| `--output` | Output file path | `--output "leads.csv"` |
| `--max-records` | Maximum records limit | `--max-records 1000` |
| `--google-sheet-id` | Google Sheets integration | `--google-sheet-id "abc123"` |
| `--verbose` | Enable detailed logging | `--verbose` |

## 🔧 Configuration

### Environment Variables (.env)

Create a `.env` file in the project root:

```env
# Google Sheets Integration (Optional)
GOOGLE_SHEETS_CREDENTIALS_PATH=path/to/credentials.json
GOOGLE_SHEETS_DEFAULT_ID=your_sheet_id_here

# Scraping Configuration
DEFAULT_MAX_RECORDS=1000
SCRAPE_DELAY_SECONDS=1

# Scheduling Configuration
WEEKLY_SCRAPE_TIME=08:00
WEEKLY_SCRAPE_DAY=monday

# Output Configuration
OUTPUT_DIRECTORY=outputs
LOG_DIRECTORY=logs
```

### Google Sheets Integration

1. Create a Google Cloud Project and enable the Sheets API
2. Create service account credentials
3. Download the JSON credentials file
4. Set `GOOGLE_SHEETS_CREDENTIALS_PATH` in your `.env` file
5. Share your Google Sheet with the service account email

## 📅 Weekly Automation

### Windows Task Scheduler

1. Run the setup script to generate the XML file
2. Import the task:

   ```cmd
   schtasks /create /xml realtor_automation_task.xml /tn "Realtor Directory Automation"
   ```

3. The task will run every Monday at 8:00 AM

### Manual Scheduler

Start the built-in Python scheduler:

```bash
python realtor_automation.py --mode schedule
```

This runs continuously and executes the scrape every Monday at 8:00 AM.

## 📁 Output Structure

### CSV Format

Generated CSV files contain the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `name` | Full name of the agent | "John Smith" |
| `email` | Email address | "<john.smith@realty.com>" |
| `phone` | Phone number | "(555) 123-4567" |
| `business_name` | Real estate company | "ABC Realty Group" |
| `address` | Business address | "123 Main St, City, ST 12345" |
| `scraped_at` | Timestamp of extraction | "2025-06-30T10:30:00" |

### File Naming

- Manual runs: `realtor_leads_YYYYMMDD_HHMMSS.csv`
- Interactive runs: `realtor_leads_interactive_YYYYMMDD_HHMMSS.csv`
- Scheduled runs: `realtor_leads_YYYYMMDD_HHMMSS.csv`
- Latest symlink: `realtor_leads_latest.csv`

## 🐛 Troubleshooting

### Common Issues

#### Chrome Driver Issues

```bash
# Update Chrome driver
pip install --upgrade webdriver-manager
```

#### Permission Errors (Windows)

```cmd
# Run as Administrator or use copy instead of symlink
# This is handled automatically by the system
```

#### Google Sheets Authentication

```bash
# Verify credentials file path
# Ensure service account has access to the sheet
# Check that the Sheets API is enabled
```

### Debug Mode

Enable verbose logging:

```bash
python realtor_automation.py --mode once --verbose
```

Check log files:

- `logs/lead_extraction_log.txt` - Scraping results
- `logs/automation_scheduler.log` - Scheduler activity
- `logs/scheduler.log` - PowerShell scheduler logs

## 🔧 Advanced Usage

### Custom Search Parameters

When using interactive mode or Python integration:

```python
search_params = {
    "state": "CA",           # State code
    "city": "Los Angeles",   # City name
    "specialty": "luxury",   # Agent specialty
    "zipcode": "90210"       # ZIP code
}
```

### Batch Processing

Process multiple regions:

```python
regions = [
    {"state": "CA", "city": "Los Angeles"},
    {"state": "NY", "city": "New York"},
    {"state": "TX", "city": "Houston"}
]

for region in regions:
    output_file = f"leads_{region['state']}_{region['city']}.csv"
    scrape_realtor_directory(
        output_path=output_file,
        search_params=region,
        max_records=500
    )
```

### Google Sheets Automation

```python
# Upload to different sheets based on region
for region in regions:
    sheet_id = get_regional_sheet_id(region['state'])
    scrape_realtor_directory(
        search_params=region,
        google_sheet_id=sheet_id
    )
```

## 📊 Monitoring & Analytics

### Log Analysis

Parse log files for performance metrics:

```python
import json

with open('logs/lead_extraction_log.txt', 'r') as f:
    for line in f:
        if line.startswith('{'):
            log_entry = json.loads(line)
            print(f"Date: {log_entry['timestamp']}")
            print(f"Leads: {log_entry['leads_found']}")
            print(f"Duration: {log_entry['duration_seconds']}s")
```

### Performance Tracking

Monitor scraping performance over time:

- Lead extraction rates
- Success/failure ratios
- Average processing time
- System resource usage

## 🛡️ Best Practices

### Ethical Scraping

- Respect robots.txt guidelines
- Use reasonable delays between requests
- Don't overload the target server
- Only scrape publicly available information

### Data Management

- Regular backups of lead data
- Data retention policies
- Privacy compliance (GDPR, CCPA)
- Secure handling of personal information

### System Maintenance

- Regular dependency updates
- Log file rotation
- Monitor disk space usage
- Test automation regularly

## 🆘 Support

### Getting Help

1. Check the troubleshooting section above
2. Review log files for error details
3. Verify your configuration settings
4. Test with a small record limit first

### Error Reporting

When reporting issues, include:

- Operating system and version
- Python version
- Error messages from logs
- Steps to reproduce the issue
- Configuration details (without sensitive data)

## 📄 License

This project is part of the bar-directory-recon system and follows the same licensing terms.

---

**Last Updated**: June 30, 2025
**Version**: 1.0.0
