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
import json
import os


def emit_status_json(site_name: str, status_data: dict, output_path: str = "output/output_status.json") -> None:
    """Emit a JSON file with site status for CI/alerting."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    payload = {
        "site": site_name,
        "status": status_data,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
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
new file:   universal_recon/README_phase_25.md
new file:   universal_recon/utils/output_status_emitter.py
```

---

## ✅ Next Actions for Team

### Python

- [ ] Call `emit_status_json` in the main workflow with `--emit-status` flag
- [ ] Confirm matrix collector supports passing `status_data`

### ADA & Agent

- [ ] Extend `validation_matrix.yaml` if needed

---

## 🔚 Summary

Phase 25 closes the loop: validator drift → suppression → CI alert via emitted JSON.

```

---

Let me know once you've saved this, and I’ll prep the `output_status_emitter.py` script and final Phase 25 patch instructions!
