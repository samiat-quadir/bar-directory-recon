# README_phase_28.md

## 🧭 Phase 28 — CI & Dashboard Integration

**Kickoff Date**: 2025-05-03  
**Current Branch**: `feature/phase-28-dashboard-init`  
**Owner**: Director (GitMo-coordinated execution)

---

### 🎯 Objectives

- Enable HTML dashboard deployment via CI
- Integrate validator risk overlays into `drift_dashboard_generator.py`
- Complete test suite coverage for new reporting modules
- Normalize `env` sync and interpreter settings across devices
- Patch `plugin_usage_diff.py` and `sync_env.py` with full CLI support

---

### 🔗 Key Links

- **CI Badge**: [![](https://github.com/YOUR_REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_REPO/actions)
- **Live Dashboards**: `docs/` folder or Netlify (TBD)
- **Suppression Matrix**: `output/risk_overlay.json`
- **Validator Rules**: `universal_recon/validators/validator_tiers.yaml`

---

### 📂 New Artifacts This Phase

| Artifact                          | Purpose                               |
|----------------------------------|----------------------------------------|
| `.env.template`                  | Shared environment config scaffold     |
| `tools/sync_env.py`              | Auto-swap `.env` based on device       |
| `output/risk_overlay.json`       | JSON summary of validator suppression  |
| `drift_dashboard_generator.py`   | Tooltip- and badge-aware overlay logic |
| `test_drift_dashboard_generator.py` | Sanity test coverage for dashboard    |

---

### ✅ Deliverables by Role

| Role     | Task Summary                                                 |
|----------|--------------------------------------------------------------|
| GitMo    | CI verification, linting, environment validation             |
| Claude   | Dashboards, README, tooltip rendering, test harness          |
| Python   | Parameterize CLI tools, extend test coverage                 |
| ADA      | Enrich suppression metadata and drift specs                  |

---

### 🛠️ Setup Notes

- Ensure Python 3.12.x is pinned in `.vscode/settings.json`
- Run `python tools/sync_env.py` before any recon CLI operation
- To regenerate dashboards:
  ```bash
  python universal_recon/main.py --site utah_bar --full-report --emit-risk-overlay --emit-drift-dashboard
