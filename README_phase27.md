# Phase 27 Overview – Scoring Suppression Tiers, Lint Cleanup, and CI Unification

## ✨ Objective
Unify validator drift scoring tiers, document overlay logic, and stabilize the project for CI enforcement and documentation clarity.

---

## 🌊 Validator Suppression Tiers
ADA and Claude now support the following YAML scoring bands, which will be used in drift overlays and suppression logic:

```yaml
validator_tiers:
  critical:  { suppression_factor: 0.80, badge: "🔴", label: "Critical Validator Removed" }
  warning:   { suppression_factor: 0.90, badge: "🟧", label: "Important Validator Removed" }
  info:      { suppression_factor: 1.00, badge: "🟩", label: "Optional Validator Removed" }
```

Each validator in `validation_matrix.yaml` may now include:
```yaml
  tier: critical | warning | info
  suppression_reason: "This validator detects missing bar numbers."
```

---

## 🌐 Overlay Outputs
Claude and Python emit the following overlay and drift artifacts:

- `output/validator_drift_overlay.html`
- `output/drift_dashboard.html`
- `output/output_status.json`
- `output/validator_drift_overlay.json`
- (Coming soon) `output/risk_overlay.json` and `risk_overlay.html`

Each site is scored with:
- `site_health`: ok | warning | degraded
- `score_suppressed_by`: float (e.g., 0.10)
- `plugins_removed`: [...]
- (Optional) `validator_drift_reason`: explanation string

---

## 🌟 Phase 27 Goals

1. 📂 **Refactor for CI Compliance**
   - Add docstrings and type annotations
   - Eliminate flake8 and mypy errors (Copilot Agent assists)
   - Inject `.copilot/config.json` for type check tuning

2. 🔢 **Emit Risk Overlay**
   - Claude drops `risk_overlay_emitter.py`
   - Shows per-site suppression by tier with reasons and tooltips

3. ⚖️ **CI Gating Logic**
   - Suppression > 20% ➞ red badge or CI soft-fail
   - Missing critical plugins ➞ triggers warning overlay

4. 📊 **Trend Integration**
   - Claude may inject suppression trends into `trend_dashboard.html`
   - Optional: add validator heatmap or delta sparkline

---

## 🚀 Launch Trigger
Phase 27 formally begins after:
- `chore/restore-hotfix-scripts` is merged to `main`
- `plugin_usage_diff.py` and overlays pass CLI smoke-test
- CI linting roadmap confirmed by Copilot

Stay tuned for overlay badge updates and CI scoring controls in this next phase.
