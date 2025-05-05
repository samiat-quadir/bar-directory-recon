# 📄 README — Phase 26: Validator Drift & Plugin Loss Dashboard

## Overview
Phase 26 introduces a unified **Drift Dashboard** for monitoring:
- Site-wide validator drift (missing required plugins)
- Plugin decay (loss of plugins between runs)
- Site health status (`ok`, `degraded`, or `critical`)

This dashboard consolidates previously separate overlays into a single HTML view.

---

## 📈 How to Generate the Drift Dashboard

### Manual CLI Run:

python analytics/drift_dashboard_generator.py

or from main.py:

python main.py --emit-drift-dashboard
s
🗂️ Files Produced
output/drift_dashboard.html
→ Colored HTML table with per-site validator/plugin health.

output/output_status.json
→ Raw JSON with drift data:

validator_drift (bool)

plugins_removed (list)

site_health (ok, degraded, critical)

🧠 What the Dashboard Shows

Site	Health	Validator Drift	Plugins Removed
utah_bar	degraded	Yes	email_plugin, form_autofill
arizona_bar	ok	No	None
🟩 ok → No validator or plugin loss.

🟧 degraded → Some validators/plugins missing (warnings).

🟥 critical → Critical validators/plugins missing.

⚙️ Internal Mechanics
Reads output/output_status.json

Maps site health to badge colors

Supports optional per-site filtering for drift dashboard if needed later

Fully CLI-safe and can be run in GitHub Actions, Cron, or Task Scheduler

🔮 Future Extensions
Add sortable table headers (by health, drift, plugin count)

Add sparklines for score trend tracking

Auto-embed suppression % tooltips if validator plugins are lost

✅ Phase 26 Summary
The drift dashboard makes it easy to spot regressions across hundreds of bar directories automatically, fueling CI triggers and badge alerts for Phase 27.
