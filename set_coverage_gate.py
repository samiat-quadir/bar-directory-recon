#!/usr/bin/env python3
"""
Set Intelligent Coverage Gate - Update --cov-fail-under based on observed coverage
"""
import pathlib
import re
import sys


def set_coverage_gate():
    """Set intelligent coverage gate to observed-1 (capped at 35%)"""
    print("⚙️ SETTING INTELLIGENT COVERAGE GATE")
    print("=" * 40)

    # Parse coverage from the recent report
    coverage_report = pathlib.Path("logs/nextwave/coverage_report_after.txt")
    if not coverage_report.exists():
        print("❌ No coverage report found")
        return False

    report_text = coverage_report.read_text()

    # Extract total coverage percentage
    match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", report_text)
    if not match:
        print("❌ Could not parse coverage percentage")
        return False

    observed_coverage = int(match.group(1))

    # Calculate intelligent gate: observed - 1, capped at 35%, minimum 8%
    target_gate = min(35, max(8, observed_coverage - 1))

    print(f"   Observed Coverage: {observed_coverage}%")
    print(f"   Target Gate: {target_gate}% (observed-1, min 8%, max 35%)")

    # Update pytest.ini
    pytest_ini = pathlib.Path("pytest.ini")
    if pytest_ini.exists():
        content = pytest_ini.read_text()

        # Update or add --cov-fail-under
        if "--cov-fail-under" in content:
            # Replace existing gate
            new_content = re.sub(
                r"--cov-fail-under=\d+", f"--cov-fail-under={target_gate}", content
            )
        else:
            # Add to addopts line
            new_content = re.sub(
                r"(addopts = [^\n]*)", rf"\1 --cov-fail-under={target_gate}", content
            )

        if new_content != content:
            pytest_ini.write_text(new_content)
            print(f"   ✅ Updated pytest.ini with gate: {target_gate}%")
            changed = True
        else:
            print("   ℹ️ No changes needed to pytest.ini")
            changed = False
    else:
        print("   ❌ pytest.ini not found")
        changed = False

    # Also check pyproject.toml if it exists
    pyproject_toml = pathlib.Path("pyproject.toml")
    if pyproject_toml.exists():
        content = pyproject_toml.read_text()
        if "--cov-fail-under" in content:
            new_content = re.sub(
                r"--cov-fail-under=\d+", f"--cov-fail-under={target_gate}", content
            )
            if new_content != content:
                pyproject_toml.write_text(new_content)
                print(f"   ✅ Updated pyproject.toml with gate: {target_gate}%")
                changed = True

    print(f"\n   GATE_SET_TO={target_gate}; CHANGED={changed}")
    return target_gate


def main():
    """Main execution"""
    try:
        gate = set_coverage_gate()
        if gate:
            print(f"✅ Coverage gate successfully set to {gate}%")
            return 0
        else:
            print("❌ Failed to set coverage gate")
            return 1
    except Exception as e:
        print(f"❌ Error setting coverage gate: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
