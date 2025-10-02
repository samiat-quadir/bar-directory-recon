# Security Notes

This document outlines security considerations and dependency management for the bar-directory-recon project.

## Security Constraints

- Dependencies are locked via `requirements-lock.txt` for reproducible builds
- Security scans run automatically via pip-audit workflow
- Known vulnerabilities are tracked and addressed promptly

## Lock Flow and Refresh Cadence

- **Lock Refresh**: Automated weekly on Wednesdays at 09:30 ET
- **Lock Verification**: Hash verification on every CI run
- **Dependency Updates**: Automated via Dependabot with security priority

## Security Scanning

- **pip-audit**: Runs on every PR and push to main
- **Bandit**: Static security analysis for Python code
- **CodeQL**: Advanced code analysis for vulnerability detection

## Reporting Security Issues

Please report security vulnerabilities via GitHub Security Advisories or contact the maintainers directly.