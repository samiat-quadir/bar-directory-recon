# Security Policy

- Findings: open an issue with label `security` or email maintainer.
- Weekly SCA: pip-audit runs Sundays 03:00 UTC; HIGH will fail.
- Code scanning: CodeQL runs on PRs and weekly; non-blocking during observation.
- Secrets: use GitHub Secrets/.env; never commit secrets.