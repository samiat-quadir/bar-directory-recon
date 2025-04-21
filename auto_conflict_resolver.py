import subprocess
from pathlib import Path

# Define files with conflicts from `git status`
conflicted_files = [
    ".gitignore",
    "git_commit_notify.log",
    "repo_tree.txt",
    "universal_recon/analytics/assets/style_overlay.css",
    "universal_recon/analytics/domain_anomaly_flagger.py",
    "universal_recon/analytics/overlay_visualizer.py",
    "universal_recon/analytics/plugin_registry_dashboard.py",
    "universal_recon/analytics/schema_dashboard_stub.py",
    "universal_recon/analytics/schema_matrix_collector.py",
    "universal_recon/analytics/schema_score_linter.py",
    "universal_recon/analytics/score_drift_export.py",
    "universal_recon/analytics/site_schema_collector.py",
    "universal_recon/analytics/trend_badge_tracker.py",
    "universal_recon/analytics/validator_drift_overlay.py",
    "universal_recon/core/output_manager.py",
    "universal_recon/main.py",
    "universal_recon/plugin_aggregator.py",
    "universal_recon/plugin_loader.py",
    "universal_recon/run_phase_21b_analysis.py",
    "universal_recon/validators/fieldmap_domain_linter.py",
    "universal_recon/validators/fieldmap_validator.py",
    "universal_recon/validators/run_phase_21b_analysis.py"
]

# Resolve each file by choosing "ours" version
for file in conflicted_files:
    try:
        subprocess.run(["git", "checkout", "--ours", file], check=True)
        subprocess.run(["git", "add", file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to resolve {file}: {e}")

print("✅ Basic conflicts resolved. Run `git rebase --continue` when ready.")
