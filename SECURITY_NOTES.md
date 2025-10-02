# Security Notes

## Scheduled refresh (weekly)
We run .github/workflows/lock-refresh.yml every Wednesday 09:30 ET (13:30 UTC).
The workflow:
1. Copies the latest constraints/*.txt to a new constraints/YYYY-MM-DD.txt.
2. Updates equirements.in to reference the new constraints file.
3. Runs pip-compile --generate-hashes to regenerate equirements-lock.txt.
4. Opens a draft PR with a short lock delta table (top 5 changes).