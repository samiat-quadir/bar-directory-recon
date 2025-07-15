# List Discovery Agent - Phase 4

## Overview

The List Discovery Agent is an intelligent web monitoring system that automatically discovers and downloads new file uploads from city and county websites. It continuously monitors configured web pages for new PDF, CSV, and Excel files containing liquor license data, business permits, and other relevant documents.

## Features

### 🔍 **Web Page Monitoring**
- Monitors multiple city/county websites simultaneously
- Detects new file uploads through change detection
- Supports PDF, CSV, XLS, and XLSX file formats
- Configurable check intervals (hourly, daily, etc.)

### 📥 **Automatic Downloads**
- Downloads new files to the input directory
- Adds timestamps to prevent filename conflicts  
- Integrates with existing pipeline automation
- Validates file types before downloading

### 📢 **Smart Notifications**
- Discord webhook notifications for new discoveries
- Email alerts with file details
- Rich formatting with file lists and metadata
- Success, warning, and error notifications

### ⚙️ **Configuration Management**
- YAML-based configuration files
- Easy URL management (add/remove/list)
- Customizable file extensions and intervals
- Advanced settings for request handling

### 🖥️ **CLI Interface**
- Interactive batch script menu
- Command-line arguments for automation
- Status reporting and statistics
- Integration with Universal Project Runner

## Quick Start

### 1. Setup
```bash
# Run the setup wizard
RunListDiscovery.bat setup

# Or manually install dependencies
pip install -r list_discovery/requirements.txt
```

### 2. Configure URLs
```bash
# Add a URL to monitor
RunListDiscovery.bat add "https://county.gov/licenses" "County Licenses"

# Edit config file directly
notepad list_discovery/config.yaml
```

### 3. Run Discovery
```bash
# Single check for new files
RunListDiscovery.bat check

# Continuous monitoring
RunListDiscovery.bat monitor
```

## Configuration

### Basic Configuration (`list_discovery/config.yaml`)

```yaml
# URLs to monitor
monitored_urls:
  - url: https://example-county.gov/licenses
    name: "Example County Liquor Licenses"

# Download settings
download_dir: "input/discovered_lists"
file_extensions: [".pdf", ".csv", ".xls", ".xlsx"]
check_interval: 3600  # 1 hour

# Notifications
notifications:
  discord_webhook: "https://discord.com/api/webhooks/..."
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    username: "your-email@gmail.com"
    recipients: ["admin@company.com"]
```

### Advanced Settings

```yaml
advanced:
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
  request_timeout: 60
  request_delay: 2
  max_file_size: 100  # MB
```

## Usage Examples

### Command Line Interface

```bash
# Interactive menu
RunListDiscovery.bat

# Direct commands
RunListDiscovery.bat check
RunListDiscovery.bat status
RunListDiscovery.bat add "https://city.gov/permits"
RunListDiscovery.bat remove 1
```

### Python API

```python
from list_discovery.agent import ListDiscoveryAgent

# Initialize agent
agent = ListDiscoveryAgent()

# Run single check
files = await agent.run_single_check()

# Add URL programmatically
agent.add_url("https://county.gov/licenses", "County Licenses")

# Get statistics
stats = agent.monitor.get_statistics()
```

### Integration with Universal Runner

The List Discovery Agent integrates seamlessly with the Universal Project Runner:

```python
# In automation/universal_runner.py
from list_discovery.agent import ListDiscoveryAgent

async def run_list_discovery():
    agent = ListDiscoveryAgent()
    new_files = await agent.run_single_check()
    
    if new_files:
        # Trigger main pipeline processing
        await run_main_pipeline()
```

## File Organization

```
list_discovery/
├── agent.py              # Main discovery agent
├── config.yaml           # Configuration file
├── requirements.txt      # Python dependencies
├── state.json            # Monitoring state (auto-generated)
└── README.md             # This documentation

input/
└── discovered_lists/     # Downloaded files
    ├── county_licenses_20240101_120000.pdf
    └── city_permits_20240101_120030.csv
```

## State Management

The agent maintains persistent state in `list_discovery/state.json`:

```json
{
  "last_check": "2024-01-01T12:00:00",
  "discovered_files": {
    "https://county.gov/licenses": [
      "https://county.gov/files/licenses_2024.pdf"
    ]
  },
  "page_hashes": {
    "https://county.gov/licenses": "abc123..."
  },
  "download_history": [
    {
      "url": "https://county.gov/files/licenses_2024.pdf",
      "filename": "licenses_2024.pdf",
      "source_page": "https://county.gov/licenses",
      "downloaded_path": "input/discovered_lists/licenses_2024_20240101_120000.pdf",
      "timestamp": "2024-01-01T12:00:00"
    }
  ]
}
```

## Monitoring and Logging

### Log Files
- `logs/automation/list_discovery.log` - Detailed operation logs
- Includes discovery events, download status, and errors
- Integrated with main automation logging system

### Status Dashboard
The List Discovery Agent status is included in the main automation dashboard:
- Files discovered today/week/month
- Active monitoring URLs
- Recent download activity
- Error reports and alerts

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install aiohttp aiofiles beautifulsoup4 PyYAML
   ```

2. **Permission Denied**
   - Check download directory permissions
   - Ensure write access to `input/discovered_lists/`

3. **Website Blocking Requests**
   - Adjust `user_agent` in configuration
   - Increase `request_delay` to be more respectful
   - Some sites may require additional headers

4. **Files Not Downloading**
   - Check file extension filters
   - Verify URL accessibility
   - Review logs for specific error messages

### Debug Mode

Enable verbose logging:

```bash
# Set environment variable
set LOGLEVEL=DEBUG
python list_discovery/agent.py check
```

## Best Practices

### 1. Respectful Monitoring
- Use reasonable check intervals (1+ hours)
- Include delays between requests
- Use appropriate user agents
- Respect robots.txt files

### 2. Configuration Management
- Regularly backup configuration files
- Document URL sources and purposes
- Monitor for broken/moved URLs

### 3. File Management
- Regular cleanup of old downloaded files
- Monitor disk space usage
- Organize files by date/source

### 4. Error Handling
- Monitor logs for recurring errors
- Set up alerts for failed downloads
- Have fallback plans for critical sources

## Integration Points

### With Universal Project Runner
- Discovered files trigger main pipeline
- Shared notification system
- Common configuration management
- Unified logging and monitoring

### With External Systems
- Discord/Slack notifications
- Email alerts and reports
- Database logging for analytics
- API endpoints for external triggers

## Security Considerations

1. **Configuration Security**
   - Store sensitive data (API keys, passwords) securely
   - Use environment variables for credentials
   - Restrict file permissions on config files

2. **Download Safety**
   - Validate file types and sizes
   - Scan downloaded files for malware
   - Quarantine suspicious downloads

3. **Network Security**
   - Use HTTPS when available
   - Validate SSL certificates
   - Consider VPN/proxy for sensitive sources

## Future Enhancements

### Planned Features
- JavaScript rendering for dynamic pages
- Content analysis and filtering
- Duplicate detection across sources
- Advanced scheduling options
- REST API interface

### Advanced Monitoring
- Content change alerts (not just new files)
- Structured data extraction
- Pattern recognition for new data types
- Machine learning for source discovery

## Support and Maintenance

### Regular Tasks
- Update URL configurations
- Review and clean logs
- Monitor disk space usage
- Test notification systems

### Updates and Patches
- Check for dependency updates
- Review security advisories
- Update user agents as needed
- Monitor source website changes

## Performance Metrics

The List Discovery Agent tracks:
- URLs monitored
- Files discovered per day/week/month
- Download success rates
- Response times and errors
- Storage usage and cleanup needs

These metrics are available through the status command and integrated into the main automation dashboard.
