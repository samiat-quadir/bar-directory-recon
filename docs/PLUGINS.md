# Plugins

This project supports a **plugin-based** scraping architecture.

## Structure
- Each plugin lives under src/<namespace>/plugins/<industry>/.
- A plugin exposes a uniform entrypoint (e.g., un(query, **opts)).
- Validation and normalization happen via the universal pipeline.

## Registration
- Plugins may be listed in plugin_registry.json for discovery by tools and docs.
- Minimal schema: { ""plugins"": [ { ""name"": ""bar"", ""path"": ""src/universal_recon/plugins/bar"" } ] }

## Guidelines
- Keep network I/O async-ready where possible.
- Add tests/fixtures; avoid hard-coded credentials; rely on config/env.