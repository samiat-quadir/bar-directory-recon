# tools/phase_execution_checker.py
from pathlib import Path

REQUIRED_ARTIFACTS = [
    "README_phase_28.md",
    "output/risk_overlay.json",
    "tools/sync_env.py",
    "universal_recon/tests/test_drift_dashboard_generator.py",
]

CI_WORKFLOWS = [".github/workflows/flow_runner.yml", ".github/workflows/dashboard_deploy.yml"]


def check_files(paths):
    missing = []
    for p in paths:
        if not Path(p).exists():
            missing.append(p)
    return missing


def main():
    print("🧪 Phase Execution QA Checker\n")

    print("📂 Checking required artifacts...")
    missing_artifacts = check_files(REQUIRED_ARTIFACTS)
    print("  ✅ All artifacts present" if not missing_artifacts else "  ❌ Missing: " + ", ".join(missing_artifacts))

    print("\n⚙️ Checking CI workflow files...")
    missing_ci = check_files(CI_WORKFLOWS)
    print("  ✅ All workflows present" if not missing_ci else "  ❌ Missing: " + ", ".join(missing_ci))

    print("\n📌 Done.\n")


if __name__ == "__main__":
    main()
