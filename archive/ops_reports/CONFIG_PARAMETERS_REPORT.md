# Configuration Parameters Report
**Generated:** 2025-07-14
**Purpose:** Complete analysis of all config.yaml parameters, types, and defaults

## 📋 Summary Overview

| Configuration File | Parameters | Defaults Set | Environment Variables |
|-------------------|------------|--------------|----------------------|
| `automation/config.yaml` | 15 primary sections | 13 with defaults | 6 supported |
| `list_discovery/config.yaml` | 6 primary sections | 5 with defaults | 5 supported |
| `universal_recon/validators/validation_matrix.yaml` | Schema validation | N/A | 0 |

## 🔧 automation/config.yaml (110 lines)

### Scheduling Configuration
```yaml
schedules:
  scraping:
    frequency: daily           # Type: string, Options: [hourly, daily, weekly]
    time: "02:00"             # Type: string, Format: HH:MM

  validation:
    frequency: daily           # Type: string, Default: daily
    time: "06:00"             # Type: string, Default: 06:00

  export:
    frequency: weekly          # Type: string, Default: weekly
    time: "23:00"             # Type: string, Default: 23:00
    day: sunday               # Type: string, Options: [monday-sunday]

  dashboard_update:
    frequency: hourly          # Type: string, Default: hourly

  list_discovery:
    enabled: true              # Type: boolean, Default: true
    frequency: hourly          # Type: string, Default: hourly
    time: "10:00"             # Type: string, Default: 10:00
```

### Monitoring Configuration
```yaml
monitoring:
  input_directories:           # Type: array[string]
    - "input/"                # Default directories
    - "snapshots/"

  file_patterns:              # Type: array[string]
    - "*.json"                # Default patterns
    - "*.csv"
    - "*.html"

  auto_process: true          # Type: boolean, Default: true
  batch_delay: 300           # Type: integer, Unit: seconds, Default: 300
```

### Notification Configuration
```yaml
notifications:
  discord_webhook: null       # Type: string|null, Env: AUTOMATION_DISCORD_WEBHOOK

  email:
    enabled: false           # Type: boolean, Default: false, Env: AUTOMATION_EMAIL_ENABLED
    smtp_server: null        # Type: string|null, Env: AUTOMATION_EMAIL_SMTP_SERVER
    smtp_port: 587          # Type: integer, Default: 587
    username: null          # Type: string|null, Env: AUTOMATION_EMAIL_USERNAME
    password: null          # Type: string|null, Env: AUTOMATION_EMAIL_PASSWORD
    recipients: []          # Type: array[string], Default: empty
```

### Dashboard Configuration
```yaml
dashboard:
  google_sheets:
    enabled: false           # Type: boolean, Default: false
    spreadsheet_id: null     # Type: string|null, Env: AUTOMATION_GOOGLE_SHEETS_ID
    credentials_path: null   # Type: string|null, Env: AUTOMATION_GOOGLE_SHEETS_CREDENTIALS

  local_html:
    enabled: true            # Type: boolean, Default: true
    output_path: "output/dashboard.html"  # Type: string, Default path
```

### Pipeline Configuration
```yaml
pipeline:
  sites: []                  # Type: array[string], Default: empty

  default_flags:             # Type: array[string]
    - "--schema-matrix"      # Default flags
    - "--emit-status"
    - "--emit-drift-dashboard"

  timeout: 3600             # Type: integer, Unit: seconds, Default: 1 hour
  retry_count: 3            # Type: integer, Default: 3
```

## 🕵️ list_discovery/config.yaml (56 lines)

### URL Monitoring Configuration
```yaml
monitored_urls: []           # Type: array[object], Default: empty
# Structure:
# - url: string              # Required: Target URL
#   name: string             # Required: Descriptive name
```

### Download Configuration
```yaml
download_dir: "input/discovered_lists"  # Type: string, Default path
file_extensions:             # Type: array[string]
  - ".pdf"                  # Default extensions
  - ".csv"
  - ".xls"
  - ".xlsx"
```

### Timing Configuration
```yaml
check_interval: 3600         # Type: integer, Unit: seconds, Default: 1 hour
```

### Notification Configuration
```yaml
notifications:
  discord_webhook: null      # Type: string|null, Env: LIST_DISCOVERY_DISCORD_WEBHOOK

  email:
    enabled: false          # Type: boolean, Default: false
    smtp_server: "smtp.gmail.com"  # Type: string, Default: Gmail
    smtp_port: 587          # Type: integer, Default: 587
    username: ""            # Type: string, Env: LIST_DISCOVERY_EMAIL_USERNAME
    password: ""            # Type: string, Env: LIST_DISCOVERY_EMAIL_PASSWORD
    from_email: ""          # Type: string, Env: LIST_DISCOVERY_EMAIL_FROM
    recipients: []          # Type: array[string], Default: empty
```

### Advanced Configuration
```yaml
advanced:
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  # Type: string, Default: Chrome user agent

  request_timeout: 60        # Type: integer, Unit: seconds, Default: 60
```

## 🎯 Environment Variable Mapping

### Current Environment Variables Used
```bash
# Automation Module
AUTOMATION_DISCORD_WEBHOOK=https://discord.com/api/webhooks/...
AUTOMATION_EMAIL_ENABLED=true|false
AUTOMATION_EMAIL_SMTP_SERVER=smtp.gmail.com
AUTOMATION_EMAIL_USERNAME=user@domain.com
AUTOMATION_EMAIL_PASSWORD=app-specific-password
AUTOMATION_GOOGLE_SHEETS_ID=spreadsheet_id
AUTOMATION_GOOGLE_SHEETS_CREDENTIALS=/path/to/creds.json
AUTOMATION_PIPELINE_TIMEOUT=7200

# List Discovery Module
LIST_DISCOVERY_DISCORD_WEBHOOK=https://discord.com/api/webhooks/...
LIST_DISCOVERY_EMAIL_USERNAME=user@domain.com
LIST_DISCOVERY_EMAIL_PASSWORD=app-specific-password
LIST_DISCOVERY_EMAIL_FROM=sender@domain.com
LIST_DISCOVERY_AGENT_TIMEOUT=3600
```

## 📊 Type Safety Analysis

### Pydantic Model Coverage
```python
# From automation/config_models.py
class ScheduleConfig(BaseModel):
    frequency: Literal["hourly", "daily", "weekly"]
    time: Optional[str] = None
    day: Optional[str] = None

class NotificationConfig(BaseModel):
    discord_webhook: Optional[HttpUrl] = None
    email: EmailConfig

class EmailConfig(BaseModel):
    enabled: bool = False
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    username: Optional[str] = None
    password: Optional[str] = None
    recipients: List[str] = []
```

### Validation Rules
- **URL Validation**: Discord webhooks validated as HttpUrl
- **File Path Validation**: Credentials paths checked for existence
- **Conditional Validation**: Email password required when email enabled
- **Range Validation**: Port numbers, timeouts within valid ranges

## 🔄 Configuration Loading Process

### Template Substitution
```yaml
# Template syntax: ${ENV_VAR:default_value}
discord_webhook: "${AUTOMATION_DISCORD_WEBHOOK:}"
password: "${AUTOMATION_EMAIL_PASSWORD:}"
timeout: "${AUTOMATION_PIPELINE_TIMEOUT:3600}"
```

### Loading Priority
1. **Environment Variables** (highest priority)
2. **Configuration File Values**
3. **Pydantic Model Defaults** (lowest priority)

## 📈 Recommendations for Phase 2

### Async Configuration Extensions
```yaml
# Proposed async section for automation/config.yaml
async_execution:
  enabled: true              # Type: boolean, Default: false
  max_workers: 4            # Type: integer, Default: CPU count
  semaphore_limit: 10       # Type: integer, Default: 10
  queue_size: 100          # Type: integer, Default: 100
  retry_backoff: 2.0       # Type: float, Default: 2.0 seconds
```

### Performance Monitoring
```yaml
# Proposed monitoring section
performance:
  metrics_enabled: true     # Type: boolean, Default: false
  metrics_interval: 60      # Type: integer, Unit: seconds
  apm_endpoint: null        # Type: string|null, Env: AUTOMATION_APM_ENDPOINT
  benchmark_enabled: false # Type: boolean, Default: false
```

---

**Configuration Analysis Complete**: All parameters catalogued with types, defaults, and environment variable mappings for Phase 2 async execution planning.
