# Phase 3 Automation Initiative - Complete Documentation
=========================================================

## 🎯 Overview

The Phase 3 Automation Initiative transforms the bar-directory-recon project into a fully automated, enterprise-grade reconnaissance system. This comprehensive automation suite provides:

- **Universal Project Runner**: Schedules and orchestrates all pipeline operations
- **Input Monitoring**: Automatically processes new data files as they arrive
- **Notification System**: Real-time alerts via Discord and Email
- **Status Dashboard**: Live monitoring and historical tracking
- **CLI Shortcuts**: Hotkeys and commands for rapid pipeline execution
- **Headless Operation**: Fully unattended execution with comprehensive logging

## 🚀 Quick Start

### 1. Initial Setup
```batch
# Install dependencies
RunAutomation.bat install

# Setup environment
RunAutomation.bat setup

# Validate system
RunAutomation.bat validate
```

### 2. Configuration
Edit `automation/config.yaml` to configure:
- Target sites for processing
- Notification settings (Discord/Email)
- Schedule preferences
- Dashboard options

### 3. Basic Operations
```batch
# Run pipeline for a single site
RunAutomation.bat quick example-bar.com

# Run full pipeline for all configured sites
RunAutomation.bat full

# Generate status dashboard
RunAutomation.bat dashboard

# Start monitoring for new input files
RunAutomation.bat monitor
```

## 🏗️ Architecture

### Core Components

1. **Universal Runner** (`automation/universal_runner.py`)
   - Main orchestration engine
   - Handles scheduling, monitoring, and execution
   - Manages configuration and state

2. **Notification Manager** (`automation/notifier.py`)
   - Discord webhook integration
   - HTML email notifications
   - Success/error/warning alerts

3. **Dashboard Manager** (`automation/dashboard.py`)
   - Real-time HTML dashboard generation
   - Status tracking and statistics
   - Google Sheets integration (planned)

4. **Pipeline Executor** (`automation/pipeline_executor.py`)
   - Executes universal_recon.main with proper error handling
   - Retry logic and timeout management
   - Environment validation

### File Structure
```
automation/
├── universal_runner.py      # Main automation engine
├── notifier.py             # Notification management
├── dashboard.py            # Status dashboard generation
├── pipeline_executor.py    # Pipeline execution engine
├── cli_shortcuts.py        # Command-line interface
└── config.yaml            # Configuration file

RunAutomation.bat           # Windows batch interface
AutomationHotkeys.ps1      # PowerShell hotkeys and shortcuts

input/                     # Monitored input directory
logs/automation/           # Automation logs
output/dashboard.html      # Generated status dashboard
```

## ⚙️ Configuration Guide

### Basic Configuration (`automation/config.yaml`)

```yaml
# Scheduling - when to run automated tasks
schedules:
  scraping:
    frequency: daily    # daily, weekly, hourly
    time: "02:00"      # 24-hour format
  
  validation:
    frequency: daily
    time: "06:00"
  
  export:
    frequency: weekly
    time: "23:00"
    day: sunday        # for weekly schedules

# Input Monitoring - watch for new files
monitoring:
  input_directories:
    - "input/"         # Add directories to monitor
    - "snapshots/"
  
  file_patterns:
    - "*.json"         # File types to process
    - "*.csv"
    - "*.html"
  
  auto_process: true   # Automatically process new files
  batch_delay: 300     # Wait 5 minutes before processing batch

# Notifications
notifications:
  # Discord webhook URL
  discord_webhook: "https://discord.com/api/webhooks/YOUR_WEBHOOK"
  
  # Email settings
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "your-email@gmail.com"
    password: "your-app-password"
    recipients:
      - "admin@yourcompany.com"

# Pipeline Settings
pipeline:
  sites:
    - "example-bar.com"    # Add your target sites
    - "another-bar.com"
  
  default_flags:
    - "--schema-matrix"    # Default pipeline flags
    - "--emit-status"
    - "--emit-drift-dashboard"
  
  timeout: 3600           # 1 hour timeout per site
  retry_count: 3          # Retry failed runs 3 times
```

### Advanced Configuration

#### Discord Webhook Setup
1. Go to your Discord server settings
2. Navigate to Integrations → Webhooks
3. Create a new webhook
4. Copy the webhook URL to `discord_webhook` in config.yaml

#### Email Configuration (Gmail Example)
1. Enable 2-factor authentication on your Gmail account
2. Generate an app-specific password
3. Use the app password in the configuration
4. Test with `RunAutomation.bat test`

## 🖥️ Command Reference

### Batch Commands (`RunAutomation.bat`)

| Command | Description | Example |
|---------|-------------|---------|
| `quick <site>` | Run pipeline for single site | `RunAutomation.bat quick example.com` |
| `full` | Run pipeline for all sites | `RunAutomation.bat full` |
| `monitor` | Start input monitoring | `RunAutomation.bat monitor` |
| `schedule` | Start automation scheduler | `RunAutomation.bat schedule` |
| `status` | Show system status | `RunAutomation.bat status` |
| `dashboard` | Generate status dashboard | `RunAutomation.bat dashboard` |
| `test` | Test notifications | `RunAutomation.bat test` |
| `validate` | Validate system health | `RunAutomation.bat validate` |
| `setup` | Setup environment | `RunAutomation.bat setup` |
| `install` | Install dependencies | `RunAutomation.bat install` |

### PowerShell Hotkeys

After running `AutomationHotkeys.ps1`, these shortcuts become available:

| Hotkey | Description |
|--------|-------------|
| `ur-quick [site]` | Quick pipeline run |
| `ur-full` | Full pipeline |
| `ur-monitor` | Start monitoring |
| `ur-schedule` | Start scheduler |
| `ur-status` | Show status |
| `ur-dashboard` | Generate dashboard |
| `ur-test` | Test notifications |
| `ur-validate` | Validate system |
| `ur-help` | Show help |

### CLI Shortcuts (`automation/cli_shortcuts.py`)

Direct Python interface for advanced users:

```bash
python automation/cli_shortcuts.py quick example.com
python automation/cli_shortcuts.py full --sites site1.com site2.com
python automation/cli_shortcuts.py monitor
python automation/cli_shortcuts.py dashboard
```

## 📊 Monitoring and Dashboards

### Status Dashboard

The HTML dashboard (`output/dashboard.html`) provides:

- **Real-time Status**: Current system state and recent activity
- **Statistics**: Success rates, total runs, failed attempts
- **Site Status**: Individual site health and last update times
- **Auto-refresh**: Updates every 5 minutes
- **Mobile-friendly**: Responsive design for all devices

Key metrics displayed:
- Total pipeline runs
- Success/failure counts
- Success rate percentage
- Individual site status
- Recent activity log

### Log Files

Comprehensive logging in `logs/automation/`:
- `universal_runner.log`: Main automation log
- `status.json`: Current system status (machine-readable)

## 🔄 Automated Workflows

### Daily Operations
1. **02:00** - Automated scraping runs for all configured sites
2. **06:00** - Validation and health checks
3. **Hourly** - Dashboard updates and status checks

### Weekly Operations
1. **Sunday 23:00** - Full export and archival
2. **Weekly** - Comprehensive system health report

### Input Processing
1. New files detected in `input/` directory
2. Batch processing after 5-minute delay
3. Automatic site detection and pipeline execution
4. Success/failure notifications

### Error Handling
1. Automatic retry (3 attempts with exponential backoff)
2. Detailed error logging
3. Immediate notification on critical failures
4. Dashboard status updates

## 🚨 Notification System

### Notification Types

1. **Success Notifications** (Green)
   - Pipeline completion
   - Successful file processing
   - System health confirmations

2. **Warning Notifications** (Orange)
   - Validation issues detected
   - Performance degradation
   - Configuration warnings

3. **Error Notifications** (Red)
   - Pipeline failures
   - System errors
   - Critical issues requiring attention

4. **Info Notifications** (Blue)
   - System status updates
   - Scheduled task confirmations
   - General information

### Notification Channels

#### Discord Integration
- Rich embed messages with color coding
- Detailed error information
- Timestamp and source tracking
- Mobile notifications

#### Email Integration
- HTML-formatted messages
- Plain text fallback
- Error details and logs
- Professional formatting

## 🛠️ Troubleshooting

### Common Issues

#### "Module not found" errors
```bash
# Install missing dependencies
RunAutomation.bat install

# Validate environment
RunAutomation.bat validate
```

#### Configuration errors
```bash
# Check configuration syntax
python -c "import yaml; yaml.safe_load(open('automation/config.yaml'))"

# Reset to default configuration
mv automation/config.yaml automation/config.yaml.backup
RunAutomation.bat setup
```

#### Pipeline failures
```bash
# Check system health
RunAutomation.bat validate

# Review logs
type logs\automation\universal_runner.log

# Test single site
RunAutomation.bat quick test-site.com
```

#### Notification issues
```bash
# Test notification systems
RunAutomation.bat test

# Check configuration
# Verify Discord webhook URL and email settings
```

### Debug Mode

Enable verbose logging by setting environment variable:
```batch
set UNIVERSAL_RUNNER_DEBUG=1
RunAutomation.bat status
```

### Log Analysis

Key log patterns to monitor:
- `ERROR` - Critical issues requiring attention
- `WARNING` - Potential problems
- `Pipeline completed successfully` - Successful runs
- `Notification sent` - Successful notifications

## 🔒 Security Considerations

### Credentials Management
- Store sensitive data in environment variables
- Use app-specific passwords for email
- Regularly rotate Discord webhook URLs
- Monitor access logs

### Access Control
- Limit file system permissions
- Secure log file access
- Protect configuration files
- Regular security audits

## 📈 Performance Optimization

### Resource Management
- Configure appropriate timeouts
- Monitor memory usage during batch processing
- Optimize retry strategies
- Schedule heavy operations during off-peak hours

### Scaling Considerations
- Parallel processing for multiple sites
- Database connection pooling
- Caching strategies
- Load balancing for high-volume operations

## 🔮 Future Enhancements

### Planned Features
1. **Google Sheets Integration** - Live dashboard in Google Sheets
2. **Slack Integration** - Additional notification channel
3. **REST API** - External system integration
4. **Machine Learning** - Predictive failure detection
5. **Mobile App** - Native mobile monitoring
6. **Advanced Analytics** - Trend analysis and reporting

### Extensibility
The modular architecture allows easy addition of:
- New notification channels
- Additional data sources
- Custom pipeline steps
- External integrations

## 📞 Support

### Getting Help
1. Review this documentation
2. Check log files for error details
3. Run system validation: `RunAutomation.bat validate`
4. Test individual components: `RunAutomation.bat test`

### Error Reporting
When reporting issues, include:
1. Full error message
2. Contents of `logs/automation/universal_runner.log`
3. Configuration file (sanitized)
4. System information and Python version

---

**Universal Project Runner - Phase 3 Automation Initiative**  
*Transforming bar directory reconnaissance through intelligent automation*
