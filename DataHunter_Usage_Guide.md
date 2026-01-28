# Data Hunter - Team Usage & Expansion Guide

## 🚀 Quick Start Guide

### Daily Operations

```bash
# Test the system
python test_data_hunter.py

# Run discovery once
python src\data_hunter.py --run-once

# Start daily scheduled discovery
python src\data_hunter.py --schedule

# Windows shortcut
RunDataHunter.bat
```

### Checking Results

- **Downloaded files**: Check `input/` directory
- **Logs**: Check `logs/auto_discovery.log`
- **Processing suggestions**: Check `logs/processing_suggestions_*.txt`

## ⚙️ Configuration Guide

### Adding Your Notifications

**Email Setup** (Edit `config/data_hunter_config.json`):

```json
"email": {
    "enabled": true,
    "username": "your-email@gmail.com",
    <!-- pragma: allowlist secret -->
    "password": "your-app-password",
    "to_emails": ["team@company.com"]
}
```

**Slack Setup**:

1. Create Slack webhook: <https://api.slack.com/messaging/webhooks>
2. Add to config:

```json
"slack": {
    "enabled": true,
    "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
}
```

### Adding New Data Sources

Add to `sources` array in `config/data_hunter_config.json`:

```json
{
    "name": "New-City",
    "url": "https://newcity.gov/building-inspections",
    "patterns": [
        ".*inspection.*\\.pdf",
        ".*property.*list.*\\.pdf",
        ".*building.*report.*\\.xlsx?"
    ],
    "enabled": true,
    "check_frequency_hours": 24
}
```

**Pattern Examples**:

- `.*inspection.*\\.pdf` - Any PDF with "inspection" in filename
- `.*property.*list.*\\.xlsx?` - Excel files with "property" and "list"
- `.*building.*safety.*\\.pdf` - PDFs with "building" and "safety"

## 🔄 Automated Processing Workflow

### 1. Discovery Process

- Data Hunter scans configured websites daily at 9:00 AM
- Downloads new files matching patterns
- Saves to `input/` with timestamp: `inspection_20250709_120000_miami_dade.pdf`

### 2. Processing New Files

When new files are found, process them with:

```bash
# Universal processing
python unified_scraper.py --pdf input/filename.pdf

# City-specific processing (adapt as needed)
python final_hallandale_pipeline.py

# Enhanced processing with Google Sheets export
python enhanced_processing_pipeline.py
```

### 3. Results & Export

- Processed data saved to `outputs/`
- Google Sheets export (if configured)
- Priority leads compilation

## 🔧 System Administration

### Automatic Startup (Windows)

1. **Run as Administrator**: `SetupDataHunterStartup.bat`
2. **Manual method**: Copy `StartDataHunterScheduled.bat` to Windows Startup folder

### Monitoring & Troubleshooting

- **Logs**: `logs/auto_discovery.log`
- **Status check**: `python test_data_hunter.py`
- **Manual run**: `python src\data_hunter.py --run-once`

### Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| No files downloaded | Check website URLs, patterns may need updating |
| Email not working | Verify SMTP credentials and app passwords |
| Virtual env error | Run `InstallDependencies.bat` |
| Permission errors | Run as Administrator for startup setup |

## 📊 Currently Configured Sources

1. **Miami-Dade County** - Property appraiser searches
2. **Broward County** - Building safety inspection programs
3. **Palm Beach County** - Recertification documents
4. **Hillsborough County** - Building inspections
5. **Orange County** - Building division reports
6. **Pinellas County** - Building safety documents

## 🔍 Expanding to New Counties/Cities

### Research Checklist

- [ ] Find municipal building department website
- [ ] Locate inspection/property list pages
- [ ] Identify file patterns (PDF/Excel naming conventions)
- [ ] Test URL accessibility
- [ ] Check for robots.txt restrictions

### Implementation Steps

1. **Add source to config** with appropriate patterns
2. **Test discovery**: `python src\data_hunter.py --run-once`
3. **Verify downloads** in `input/` directory
4. **Adapt processing scripts** for new city format
5. **Update documentation**

### Pattern Development Tips

- Use browser developer tools to inspect links
- Test patterns with online regex tools
- Start broad, then narrow down
- Consider file extensions: `.pdf`, `.xlsx?`, `.xls`

## 📈 Performance & Optimization

### Recommended Settings

- **Check frequency**: 24 hours (daily)
- **File size limit**: 50MB (configurable)
- **Timeout**: 30 seconds
- **Retry attempts**: 3

### Scaling Considerations

- Add more sources gradually
- Monitor disk space in `input/` directory
- Consider automated cleanup of old files
- Scale notification frequency based on volume

## 🛠️ Advanced Features

### Custom Processing Integration

```python
# Auto-trigger processing after download
def post_download_hook(new_files):
    for file in new_files:
        subprocess.run(['python', 'unified_scraper.py', '--pdf', file])
```

### Webhook Integration

- Add custom webhook endpoints for external system integration
- Trigger third-party workflows on new file discovery

### Analytics & Reporting

- Track discovery success rates by source
- Monitor file download patterns
- Generate automated discovery reports

---

## 📞 Support & Maintenance

**For issues or questions:**

1. Check `logs/auto_discovery.log`
2. Run `python test_data_hunter.py` for diagnostics
3. Review configuration in `config/data_hunter_config.json`
4. Contact system administrator

**Regular maintenance:**

- Review and update URL patterns monthly
- Clean old files from `input/` directory
- Monitor notification delivery
- Update source configurations as needed
