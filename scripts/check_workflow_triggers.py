#!/usr/bin/env python3
"""Check workflow triggers to ensure compliance with allow-list."""

import sys
import yaml
from pathlib import Path

def main():
    """Check all workflow files for proper trigger usage."""
    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        print("No workflows directory found")
        return 0
    
    # Allow-list: only these workflows can use pull_request/push triggers
    allowed_workflows = {
        "fast-parity-ci.yml",
        "pip-audit.yml"
    }
    
    # Also allow codeql*.yml/.yaml files
    violations = []
    
    for workflow_file in workflows_dir.glob("*.yml"):
        if workflow_file.name.startswith("codeql"):
            continue  # CodeQL workflows are allowed
        
        if workflow_file.name in allowed_workflows:
            continue  # Explicitly allowed
        
        try:
            content = workflow_file.read_text(encoding="utf-8")
            data = yaml.safe_load(content)
            
            if "on" in data:
                triggers = data["on"]
                if isinstance(triggers, dict):
                    if "pull_request" in triggers or "push" in triggers:
                        violations.append(f"{workflow_file.name}: uses pull_request/push trigger")
                elif isinstance(triggers, list):
                    if "pull_request" in triggers or "push" in triggers:
                        violations.append(f"{workflow_file.name}: uses pull_request/push trigger")
        except Exception as e:
            print(f"Error parsing {workflow_file.name}: {e}")
            continue
    
    if violations:
        print("Workflow trigger violations found:")
        for violation in violations:
            print(f"  - {violation}")
        print("\nOnly these workflows may use pull_request/push triggers:")
        print("  - fast-parity-ci.yml")
        print("  - pip-audit.yml") 
        print("  - codeql*.yml/.yaml")
        return 1
    
    print("All workflows comply with trigger restrictions")
    return 0

if __name__ == "__main__":
    sys.exit(main())