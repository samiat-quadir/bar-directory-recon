# copilot_prompts.md

> Purpose: Help GitHub Copilot Agent validate, repair, or extend **Universal Recon** modules based on the latest health diagnostics.

---

## 🛠 MODULE REPAIR PROMPTS

### 1. Fix Missing `emit_status()` in `status_summary_emitter.py`
```plaintext
Task: Update universal_recon/utils/status_summary_emitter.py.
Ensure it defines a callable `emit_status()` function that:
- Loads output/schema_matrix.json
- Loads validators/validation_matrix.yaml
- Writes output/output_status.json
- Can run standalone with `python status_summary_emitter.py`

Ensure the function accepts:
- matrix_path
- export_path
- verbose (optional)
```

---

### 2. Fix Missing `load_validation_matrix()` in `validation_matrix.py`
```plaintext
Task: Update universal_recon/validators/validation_matrix.py.
Define a function `load_validation_matrix()` that:
- Loads validators/validation_matrix.yaml
- Returns parsed YAML content as Python dict
- Handles missing file gracefully (prints error, returns empty dict)
```

---

## ✅ DIAGNOSTIC TEST PROMPTS

### 3. Re-run Health Bootstrap + Module Health Checker
```plaintext
Task: After fixes, re-run:
- python universal_recon/utils/health_bootstrap.py
- python universal_recon/utils/module_health_checker.py

Ensure all modules import cleanly, no missing functions.
Confirm HTML report output: output/module_health_report.html.
```

---

## 🧪 SANITY TEST PROMPTS

### 4. Quick Fieldmap Validation Test
```plaintext
Task: Create a test script to:
- Run universal_recon/analytics/site_schema_collector.collect_fieldmap()
- Target mock site (e.g., "utah_bar")
- Confirm output/fieldmap/utah_bar_fieldmap.json is created
- Print success/failure
```

### 5. Quick Validator Drift Detection Test
```plaintext
Task: Create a test script to:
- Run universal_recon/analytics/validator_drift_overlay.main()
- Confirm output/validator_drift_overlay.json exists
- Confirm output/validator_drift_overlay.html exists
- Print drift warnings if any detected
```

---

## ✨ OPTIONAL: TOOLING ENHANCEMENTS PROMPTS

### 6. Improve Health Checker with Drift Detection
```plaintext
Task: Enhance universal_recon/utils/module_health_checker.py:
- Detect if output/schema_matrix.json is older than 24h
- Warn if fieldmap or matrix are stale
- Suggest re-running main.py if matrix is missing
```

### 7. Improve Health Bootstrap with Overlay Awareness
```plaintext
Task: Enhance universal_recon/utils/health_bootstrap.py:
- Detect if plugin_decay_overlay.py or validator_drift_overlay.py can import
- Check if corresponding output HTML files exist
- Report badge: OK / Missing / Needs regeneration
```

---

# 🔥 Final Mission for Copilot Agent
Once all repairs and upgrades above are complete:
- Full CLI `python universal_recon/main.py --site utah_bar --full-report --verbose` should succeed ✅
- All overlays and output reports should be generated ✅
- All modules import cleanly ✅

Then Phase 26 can officially begin 🚀.
