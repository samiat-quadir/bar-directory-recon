**Development Setup**

- **Codespaces secret name:** `SCRAPER_API_KEY`
- Add this secret to your Codespaces repository or organization Secrets (no value in repo).
- The devcontainer maps the host environment variable into the container via `containerEnv.SCRAPER_API_KEY` in `.devcontainer/devcontainer.json`.
- Create a local `.env` from `.env.example` for local runs and set `SCRAPER_API_KEY` locally when needed.

Post-create steps executed in the container (already configured):

- `pip install -e .[dev] && pytest -q`

Local smoke run (no secrets required):

```bash
python -m pip install -e .[dev]
pytest -q
```

If Codespaces or devcontainer fails to find `SCRAPER_API_KEY`, verify you added the repository secret with name `SCRAPER_API_KEY` and that Codespaces is configured to expose repository secrets.
