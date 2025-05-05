# Phase 24 – Validator Drift & Plugin Loss Tracking

## ✅ Goal

Link plugin usage to validator health. Detect if any **required plugin** is missing, and flag **risk levels** in both JSON and HTML outputs.

---

## 🔍 New Capabilities

### 1. `plugins_used` Field
- Stored in each site's `schema_matrix.json`
- Automatically populated via `plugin_aggregator.py`

### 2. Validator Mapping (`validation_matrix.yaml`)
Each validator now supports:

```yaml
email_validator:
  plugin: email_plugin
  plugin_required: true
  on_plugin_removed: warning
  tooltip: "Plugin ensures email parsing works on contact pages."


3. Drift Risk Levels
Level	Badge	Description
critical	❌ Red	Validator is required, plugin is missing
warning	⚠️ Yellow	Plugin optional, but removal impacts scores
info	ℹ️ Blue	Informational drift only
🧠 CLI Tools & Flags
1. Generate Validator Drift Overlay
bash
Copy code
python validators/validator_drift_overlay.py
Outputs:

output/validator_drift_overlay.json

output/validator_drift_overlay.html

2. Related Flags (in main.py):
--schema-matrix

--plugin-decay

--plugin-diff

--validator-overlay

🧩 Matrix Fields (per site)
json
Copy code
{
  "plugins_used": ["email_plugin", "bar_number_annotator"],
  "score_summary": {
    "field_score": 82.3
  },
  "domain_tags": ["legal", "bar"],
  "anomaly_flags": [],
  "validator_drift": true
}
🔮 Roadmap – Phase 25+
Score suppression if critical validators go missing

CI failure if validator drift severity is critical

Tooltip badges for missing validators

Optional: emit output/output_status.json per run
