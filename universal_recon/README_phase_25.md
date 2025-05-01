Here’s your all-in-one `README_phase_25.md` markdown file, including:

- 🎯 Goals and scope for Phase 25
- 🧩 New file additions you’ll need (CLI emitter + score suppression logic)
- 🛠️ Suggested CLI exports (`output_status.json`)
- 🧪 Integration points for Copilot Agent, ADA, and Python
- 💾 Git-friendly path confirmations for current status

You can **copy and paste the entire block below** into a new file named:

```plaintext
universal_recon/README_phase_25.md
```

---

```markdown
# ✅ README_phase_25.md

## 🧠 Phase 25 — Validator Drift Severity & Score Suppression

**Status**: 🔛 ACTIVE
**Branch**: `fix-line-endings` (up to date with origin)
**Lead Modules**: validator_drift_overlay.py, schema_matrix_collector.py, plugin_decay_overlay.py

---

## 🎯 Objectives

- Introduce validator-aware score penalties in the matrix
- Generate `output/output_status.json` after each run for CI/alerting
- Overlay `validator_drift` badges and severity scores in HTML dashboards
- Begin end-to-end “drift risk → score → CI alert” pipeline

---

## 📁 Key File Additions (Patch During Phase 25)

### 1. `utils/output_status_emitter.py`

```python
# === universal_recon/utils/output_status_emitter.py ===
import json, os

def emit_status_json(site_name, status_data, output_path="output/output_status.json"):
    os.makedirs("output", exist_ok=True)
    full = {
        "site": site_name,
        "status": status_data
    }
    with open(output_path, "w") as f:
        json.dump(full, f, indent=2)
    print(f"[✓] Site status exported to: {output_path}")
```

---

### 2. Suggested Status Format

```json
{
  "site": "utah_bar",
  "status": {
    "validator_drift": true,
    "plugin_removed": ["email_plugin", "form_autofill"],
    "site_health": "degraded",
    "score_suppression": {
      "field_score_before": 0.92,
      "field_score_after": 0.83,
      "penalty_reason": "Critical validator drift"
    }
  }
}
```

---

## 🧪 Copilot Agent Task Suggestions

1. Add validator-drift suppression logic in:
   - `schema_score_linter.py` or `schema_matrix_collector.py`
   - Use ADA’s `validation_matrix.yaml` to reference which plugins are `critical`

2. Write suppression logic like:
   ```python
   if drift_severity == "critical":
       new_score = old_score * 0.90  # 10% penalty
   ```

3. Hook `emit_status_json(...)` after matrix write step

---

## 🧷 Git Confirmations

> You can safely commit now. These files are ready:
```plaintext
new file:   universal_recon/README_phase_24.md
new file:   universal_recon/validators/validator_drift_overlay.py
new file:   universal_recon/utils/validator_drift_badges.py
new file:   universal_recon/core/report_printer.py
modified:   universal_recon/plugin_aggregator.py
modified:   universal_recon/analytics/schema_matrix_collector.py
modified:   universal_recon/analytics/plugin_decay_overlay.py
modified:   universal_recon/plugins/record_field_validator_v3.py
```

---

## ✅ Next Actions for Team

### Claude:
- [ ] Add `output_status_emitter.py` (see above)
- [ ] Patch matrix collector to apply validator-based score suppression
- [ ] Optionally inject output_status into HTML overlays

### Python:
- [ ] Add `--emit-status` flag to `main.py` that calls emitter
- [ ] Confirm `score_summary.field_score` supports suppression logic
- [ ] Optionally route `output_status.json` into CI runner

### ADA:
- [ ] Extend `validation_matrix.yaml` with:
   ```yaml
   tooltip: "Plugin ensures proper parsing of bar number from unstructured formats."
   ```
- [ ] Define when score suppression is allowed (e.g. ignore `info` drift)

---

## 🔚 Summary

Phase 25 unlocks true validator risk enforcement. We now translate validator → plugin → matrix → drift → suppression → alert.

Let’s close this loop cleanly.

```

---

Let me know once you've saved this, and I’ll prep the `output_status_emitter.py` script and final Phase 25 patch instructions!
