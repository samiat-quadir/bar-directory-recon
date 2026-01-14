# Configuration Guide

This guide covers environment configuration, secrets management, and best practices for the Bar Directory Recon project.

## Table of Contents

- [Environment Setup](#environment-setup)
- [Configuration Files](#configuration-files)
- [Secrets Management](#secrets-management)
- [Device-Specific Config](#device-specific-config)
- [Security Best Practices](#security-best-practices)

---

## Environment Setup

### Quick Setup

1. **Copy the example file**:
   ```bash
   cp .env.example .env.local
   ```

2. **Edit `.env.local`** with your credentials (never commit this file!)

3. **Verify configuration**:
   ```bash
   python -c "from src.config_loader import ConfigLoader; print(ConfigLoader().as_dict())"
   ```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_SHEETS_CREDENTIALS_PATH` | For sheets export | Path to Google Sheets service account JSON |
| `GOOGLE_SHEETS_SPREADSHEET_ID` | For sheets export | Target spreadsheet ID |
| `BDR_ADAPTER_METRICS` | No | Enable adapter metrics (`0` or `1`) |
| `SLACK_WEBHOOK_URL` | No | Slack notification webhook |
| `SMTP_SERVER` | For email | SMTP server hostname |
| `SMTP_PORT` | For email | SMTP port (usually 587 or 465) |
| `EMAIL_USERNAME` | For email | SMTP authentication username |
| `EMAIL_PASSWORD` | For email | SMTP authentication password |

---

## Configuration Files

### Directory Structure

```
config/
├── data_hunter_config.json    # Data Hunter settings
├── device_config.json         # Device-specific (gitignored)
├── lawyer_directory.json      # Lawyer scraper config
├── realtor_directory.json     # Realtor scraper config
└── test_config.json           # Test environment config
```

### Config File Formats

The project uses **JSON** for configuration. Each config follows this pattern:

```json
{
  "name": "scraper_name",
  "description": "What this config does",
  "base_url": "https://example.com",
  "listing_phase": { ... },
  "detail_phase": { ... },
  "pagination": { ... },
  "data_extraction": { ... },
  "output": { ... },
  "options": { ... }
}
```

### Loading Configuration

```python
from src.config_loader import ConfigLoader

# Load default config
config = ConfigLoader()

# Load with custom path
config = ConfigLoader(config_path="config/custom.json")

# Access settings
print(config.get("base_url"))
print(config.as_dict())
```

---

## Secrets Management

### Local Development

For local development, use `.env.local`:

```bash
# .env.local (NEVER commit this file)
GOOGLE_SHEETS_CREDENTIALS_PATH=/path/to/credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

### Production (Azure Key Vault)

For production, use Azure Key Vault for secure credential storage.
See [docs/security.md](security.md) for full Azure Key Vault setup.

```python
from src.security_manager import SecurityManager

# Production: Secrets from Key Vault
security = SecurityManager()
api_key = security.get_secret("hunter-api-key")
```

### Google Sheets Credentials

1. Create a Google Cloud project
2. Enable Google Sheets API
3. Create a service account
4. Download the JSON credentials file
5. Set `GOOGLE_SHEETS_CREDENTIALS_PATH` to the file path

See [docs/GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md) for detailed setup.

---

## Device-Specific Config

The project supports multi-device development with automatic environment detection.

### How It Works

```python
# env_loader.py auto-detects device
from env_loader import load_env

# Loads appropriate .env file based on hostname:
# - .env.work     → Work machine
# - .env.asus     → ASUS device
# - .env.local    → Local development (fallback)
```

### Device Profile

Each device creates a profile in `config/device_config.json` (gitignored):

```json
{
  "device_id": "ASUS-ROG",
  "hostname": "ROG-LUCCI",
  "platform": "Windows",
  "python_version": "3.13.0",
  "last_sync": "2025-08-14T10:30:00Z"
}
```

### Cross-Device Bootstrap

For setting up a new device to match an existing configuration:

```powershell
# Windows
.\bootstrap_alienware.ps1

# Linux/macOS
./bootstrap_alienware.sh
```

---

## Security Best Practices

### ✅ DO

- Use `.env.local` for local secrets (automatically gitignored)
- Use Azure Key Vault for production credentials
- Rotate API keys regularly
- Use read-only credentials when possible
- Review access logs periodically

### ❌ DON'T

- Commit `.env` files with real credentials
- Hardcode API keys in source code
- Share credentials via chat/email
- Use production credentials in development
- Store credentials in config/*.json files

### Secrets Scanning

The project includes a secrets scanner to prevent accidental commits:

```bash
# Run secrets scan
python tools/secrets_scan.py --directory . --severity medium

# Or use the VS Code task
# Task: "Secrets Scan"
```

### Pre-commit Hook

Enable the pre-commit hook to automatically scan for secrets:

```bash
pre-commit install
pre-commit run --all-files
```

---

## Troubleshooting

### Common Issues

**Config not loading**:
```bash
# Verify config file exists and is valid JSON
python -c "import json; json.load(open('config/data_hunter_config.json'))"
```

**Environment variables not set**:
```bash
# Check if .env.local exists
ls -la .env*

# Verify variable is loaded
python -c "import os; print(os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH'))"
```

**Device config mismatch**:
```bash
# Regenerate device config
python scripts/detect_device.py --regenerate
```

### Getting Help

- Check [docs/security.md](security.md) for Azure Key Vault issues
- Check [docs/GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md) for Sheets API issues
- Open a GitHub issue for unresolved problems

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-08-14 | Initial configuration guide |
