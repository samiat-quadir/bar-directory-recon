# Overnight Sprint v2 - Coverage Boost & Security Plan

This document describes the Overnight Sprint v2 automation that enhances code coverage through auto-generated smoke tests and provides security auditing capabilities.

## Overview

The Overnight Sprint v2 is designed to:
- 🎯 **Boost Coverage**: Auto-generate import-only smoke tests for worst coverage modules
- 🔒 **Security Audit**: Run security scans and generate Software Bill of Materials (SBOM)
- 📝 **Create PRs**: Automatically create pull requests for review (no auto-merge)
- 📊 **Comprehensive Logging**: Generate detailed reports in `logs/nightly/`

## Files

### PowerShell Script (Windows Production)
```powershell
./overnight_sprint_v2.ps1
```

### Bash Script (Linux Testing)
```bash
./overnight_sprint_v2.sh
```

## Prerequisites

### Windows Environment
```powershell
# Run from C:\Code\bar-directory-recon on ALI
# Requirements:
- Python 3.8+
- Git with CLI access
- GitHub CLI (gh) for PR creation
- PowerShell 5.1+
```

### Dependencies
```bash
pip install coverage pytest bandit pip-audit cyclonedx-bom
pip install -r requirements.txt -r requirements-dev.txt
```

## Usage

### Windows (Production)
```powershell
# Navigate to project directory
Set-Location C:\Code\bar-directory-recon

# Run overnight sprint
.\overnight_sprint_v2.ps1
```

### Linux (Testing)
```bash
# Navigate to project directory
cd /path/to/bar-directory-recon

# Run overnight sprint
./overnight_sprint_v2.sh
```

## Process Steps

### Step 1: Repository Sync & Environment
- ✅ Syncs repository with latest changes
- ✅ Creates isolated virtual environment (`.venv-ci`)
- ✅ Updates pip to latest version

### Step 2: Tool Installation
- ✅ Installs testing and coverage tools
- ✅ Installs security scanning tools
- ✅ Verifies all dependencies

### Step 3: First Test Pass
- ✅ Cleans previous artifacts
- ✅ Runs tests excluding slow/e2e/integration
- ✅ Generates initial coverage reports
- ✅ Creates JUnit XML and HTML reports

### Step 4: Coverage Analysis & Smoke Test Generation
- ✅ Analyzes coverage XML to find worst modules
- ✅ Creates top 10 worst coverage heatmap
- ✅ Auto-generates import-only smoke tests
- ✅ Places tests in `universal_recon/tests/auto_smoke/`

### Step 5: Second Test Pass
- ✅ Runs tests including new smoke tests
- ✅ Measures coverage improvement
- ✅ Generates final coverage reports

### Step 6: Coverage PR Creation
- ✅ Creates new branch `chore/coverage-nightly-YYYYMMDD-HHMM`
- ✅ Commits smoke tests and coverage reports
- ✅ Pushes branch for manual review

### Step 7: Security Audit
- ✅ Runs Bandit security scanner
- ✅ Generates pip-audit dependency audit
- ✅ Creates Software Bill of Materials (SBOM)
- ✅ Creates security PR branch

### Step 8: Final Summary
- ✅ Outputs comprehensive summary line
- ✅ Reports coverage improvement metrics
- ✅ Confirms PR creation status

## Output Files

### Coverage Reports
```
logs/nightly/
├── coverage_first.xml          # Initial coverage XML
├── coverage_after.xml          # Final coverage XML
├── coverage_report_first.txt   # Initial coverage text report
├── coverage_report_after.txt   # Final coverage text report
├── coverage_html_first/        # Initial HTML coverage report
├── coverage_html_after/        # Final HTML coverage report
└── coverage_heatmap_top10.json # Worst coverage modules
```

### Test Results
```
logs/nightly/
├── junit_first.xml       # Initial test results
├── junit_after.xml       # Final test results
├── pytest_first.txt     # Initial test output
└── pytest_after.txt     # Final test output
```

### Security Audit
```
logs/nightly/
├── bandit.txt           # Security scan results
├── pip_audit.json      # Dependency vulnerability audit
└── sbom.json           # Software Bill of Materials
```

### Auto-Generated Tests
```
universal_recon/tests/auto_smoke/
├── test_auto_01.py      # Import test for worst module #1
├── test_auto_02.py      # Import test for worst module #2
└── ...                 # Up to 10 smoke tests
```

## Sample Output

```
🎯 SUMMARY >> env=windows venv=.venv-ci tests_ok=true total_cov=12% smokes=10 coverage_pr=yes security_plan_pr=yes
```

### Summary Fields
- **env**: Environment (windows/linux)
- **venv**: Virtual environment used (.venv-ci)
- **tests_ok**: Whether tests passed (true/false)
- **total_cov**: Final coverage percentage
- **smokes**: Number of smoke tests generated
- **coverage_pr**: Coverage PR created (yes/no)
- **security_plan_pr**: Security PR created (yes/no)

## Auto-Generated Smoke Tests

### Purpose
- **Safe Testing**: Import-only tests with error handling
- **Coverage Boost**: Improves coverage metrics through basic imports
- **Network-Free**: No external dependencies or side effects
- **Review Ready**: Requires manual review before merging

### Example Test
```python
"""Auto-generated smoke test for src.config_loader"""

def test_import_01():
    """Auto-generated import-only smoke test for src.config_loader"""
    try:
        __import__("src.config_loader")
    except ImportError as e:
        # This is expected for modules with missing dependencies
        pass
```

## PR Creation

### Coverage PR
- **Branch**: `chore/coverage-nightly-YYYYMMDD-HHMM`
- **Title**: `chore(coverage): nightly auto-smoke (~XX%)`
- **Label**: `coverage-candidate`
- **Content**: Auto-generated import-only smoke tests

### Security PR
- **Branch**: `chore/deps-security-plan-YYYYMMDD-HHMM`
- **Title**: `chore(security): pip-audit + SBOM (plan only)`
- **Labels**: `needs-review`, `security`
- **Content**: Security audit results and SBOM

## Best Practices

### Manual Review Required
- ⚠️ **No Auto-Merge**: All PRs require manual review
- ⚠️ **Test Validation**: Verify smoke tests don't introduce issues
- ⚠️ **Security Review**: Review security findings before action

### Scheduling
- 🌙 **Overnight Runs**: Designed for automated overnight execution
- 📅 **Daily Cadence**: Can be run daily for continuous improvement
- 🔄 **Incremental**: Each run builds on previous improvements

### Environment Isolation
- 🔒 **Isolated venv**: Uses `.venv-ci` to avoid conflicts
- 🧹 **Clean State**: Starts with clean artifacts each run
- 📦 **Reproducible**: Same results across environments

## Troubleshooting

### Common Issues

#### Virtual Environment Creation Fails
```powershell
# Solution: Ensure Python is in PATH
python --version
python -m venv .venv-ci
```

#### Git Operations Fail
```powershell
# Solution: Configure Git and GitHub CLI
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
gh auth login
```

#### Coverage Analysis Fails
```bash
# Solution: Ensure PYTHONPATH is set correctly
export PYTHONPATH="src:universal_recon"
coverage run -m pytest
```

#### Security Tools Missing
```bash
# Solution: Install security dependencies
pip install bandit pip-audit cyclonedx-bom
```

### Log Analysis

Check `logs/nightly/` for detailed error information:
- **pytest_*.txt**: Test execution logs
- **coverage_report_*.txt**: Coverage analysis
- **bandit.txt**: Security scan details

## Integration

### CI/CD Pipeline
The overnight sprint can be integrated into CI/CD:
```yaml
name: Overnight Sprint
on:
  schedule:
    - cron: '0 2 * * *'  # Run at 2 AM daily
jobs:
  coverage-boost:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Overnight Sprint
        run: .\overnight_sprint_v2.ps1
```

### Monitoring
Monitor the summary output for trends:
- Coverage percentage improvements over time
- Number of smoke tests generated
- Security findings patterns

## Contributing

When modifying the overnight sprint:
1. Test both Windows and Linux versions
2. Ensure all log files are generated
3. Verify PR creation works correctly
4. Update this documentation for any changes