# 🔍 Universal Project Runner - Phase 3 Automation Initiative

## ✨ Quick Start

**Run the demo:**
```batch
python automation_demo.py
```

**Start automating:**
```batch
RunAutomation.bat setup
RunAutomation.bat dashboard
```

## 🚀 What's New

### Universal Project Runner
- **Scheduled Operations**: Daily scraping, weekly exports, hourly status updates
- **Input Monitoring**: Auto-process new files dropped in `input/` directory
- **Smart Notifications**: Discord webhooks + HTML email alerts
- **Live Dashboard**: Real-time status with auto-refresh
- **CLI Shortcuts**: Batch scripts, PowerShell hotkeys, Python APIs

### Key Features

| Feature | Description | Command |
|---------|-------------|---------|
| 🔄 **Auto Pipeline** | Runs full pipeline for all sites | `RunAutomation.bat full` |
| ⚡ **Quick Run** | Single site processing | `RunAutomation.bat quick site.com` |
| 👀 **Input Monitor** | Watch for new data files | `RunAutomation.bat monitor` |
| ⏰ **Scheduler** | Daily/weekly automation | `RunAutomation.bat schedule` |
| 📊 **Dashboard** | Live status & statistics | `RunAutomation.bat dashboard` |
| 📧 **Notifications** | Discord/Email alerts | `RunAutomation.bat test` |

## 🛠️ Components

### Core Automation (`automation/`)
- `universal_runner.py` - Main orchestration engine
- `notifier.py` - Discord/Email notification system
- `dashboard.py` - Status dashboard generator
- `pipeline_executor.py` - Pipeline execution with retry logic
- `cli_shortcuts.py` - Command-line interface
- `config.yaml` - Configuration file

### User Interfaces
- `RunAutomation.bat` - Windows batch interface
- `AutomationHotkeys.ps1` - PowerShell shortcuts
- `automation_demo.py` - Live demonstration
- VS Code Tasks - Integrated task runner

## ⚙️ Configuration

Edit `automation/config.yaml`:

```yaml
# Add your sites
pipeline:
  sites:
    - "your-target-site.com"

# Setup notifications
notifications:
  discord_webhook: "https://discord.com/api/webhooks/..."
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    username: "your-email@gmail.com"
    recipients: ["admin@company.com"]

# Schedule automation
schedules:
  scraping:
    frequency: daily
    time: "02:00"
```

## 🎯 Use Cases

### Daily Operations
- **02:00** - Automated scraping for all sites
- **06:00** - Validation and health checks
- **Hourly** - Dashboard updates
- **Continuous** - Input file monitoring

### On-Demand Tasks
- Process urgent site updates
- Generate instant status reports
- Test notification systems
- Validate pipeline health

### Development Workflow
- Monitor for new data files
- Automatic processing and validation
- Real-time status tracking
- Error notifications

## 🔧 PowerShell Hotkeys

Load shortcuts: `. .\AutomationHotkeys.ps1`

```powershell
ur-quick site.com    # Quick pipeline run
ur-full             # Full pipeline
ur-dashboard        # Generate dashboard
ur-status          # Show status
ur-monitor         # Start monitoring
ur-help            # Show help
```

## 📊 Dashboard Features

The live dashboard (`output/dashboard.html`) shows:
- ✅ Success/failure statistics
- 📈 Success rate trending
- 🌐 Individual site status
- 📋 Recent activity log
- 🔄 Auto-refresh every 5 minutes

## 📧 Notification System

### Discord Integration
- Rich embed messages with color coding
- Error details and stack traces
- Mobile push notifications
- Instant delivery

### Email Integration
- HTML formatted messages
- Professional styling
- Error logs attached
- Multiple recipients

## 🗂️ File Organization

```
bar-directory-recon-1/
├── automation/           # 🤖 Automation engine
├── input/               # 📥 Drop files here for auto-processing
├── output/              # 📤 Generated reports and dashboard
├── logs/automation/     # 📝 Automation logs
├── RunAutomation.bat    # 🚀 Main launcher
└── automation_demo.py   # 🎬 Live demo
```

## 🚨 Error Handling

- **Automatic Retry**: 3 attempts with exponential backoff
- **Timeout Protection**: 1-hour max per operation
- **Detailed Logging**: Full error traces and context
- **Instant Alerts**: Immediate notification on failures
- **Graceful Degradation**: Continue processing other sites

## 🔮 Advanced Features

### Headless Operation
- Runs completely unattended
- Comprehensive logging for debugging
- Background process support
- Resource management

### Cross-Device Compatibility
- Works on any Windows machine
- Portable configuration
- Device-specific optimizations
- Cloud synchronization ready

## 📋 Next Steps

1. **Setup**: Run `RunAutomation.bat setup`
2. **Configure**: Edit `automation/config.yaml`
3. **Test**: Run `RunAutomation.bat test`
4. **Demo**: Run `python automation_demo.py`
5. **Deploy**: Run `RunAutomation.bat schedule`

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Module errors | `RunAutomation.bat install` |
| Config errors | `RunAutomation.bat setup` |
| Pipeline fails | `RunAutomation.bat validate` |
| No notifications | `RunAutomation.bat test` |

---

**Phase 3 Automation Initiative**
*Intelligent, scalable, hands-free bar directory reconnaissance*

🔗 **Documentation**: See `PHASE3_AUTOMATION_DOCS.md` for complete details
🎬 **Demo**: Run `python automation_demo.py` for live demonstration
⚙️ **Configuration**: Edit `automation/config.yaml` to customize
