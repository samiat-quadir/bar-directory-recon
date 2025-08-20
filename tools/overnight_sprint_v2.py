#!/usr/bin/env python3
"""
Overnight Sprint v2 - Cross-Platform Coverage and Security Automation
Windows/Linux compatible implementation of overnight sprint tasks.
"""

import os
import sys
import platform
import subprocess
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class OvernightSprintV2:
    """Cross-platform overnight sprint automation."""
    
    def __init__(self, repo_root: str = None):
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        self.is_windows = platform.system() == 'Windows'
        self.logs_dir = self.repo_root / "logs" / "nightly"
        self.venv_name = ".venv-ci"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create logs directory
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
        # Also log to file
        log_file = self.logs_dir / f"overnight_sprint_{self.timestamp}.log"
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] {level}: {message}\n")
    
    def run_command(self, command: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run command cross-platform."""
        if self.is_windows and command[0] == "python":
            # On Windows, ensure we use the virtual environment Python
            venv_python = self.repo_root / self.venv_name / "Scripts" / "python.exe"
            if venv_python.exists():
                command[0] = str(venv_python)
        elif not self.is_windows and command[0] == "python":
            # On Linux, use activated environment or system python
            venv_python = self.repo_root / self.venv_name / "bin" / "python"
            if venv_python.exists():
                command[0] = str(venv_python)
        
        self.log(f"Running: {' '.join(command)}")
        try:
            result = subprocess.run(command, cwd=self.repo_root, check=check, 
                                  capture_output=True, text=True)
            if result.stdout:
                self.log(f"STDOUT: {result.stdout[:500]}...")  # Truncate long output
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {e}", "ERROR")
            if e.stdout:
                self.log(f"STDOUT: {e.stdout}", "ERROR")
            if e.stderr:
                self.log(f"STDERR: {e.stderr}", "ERROR")
            if not check:
                return e
            raise
    
    def setup_virtual_environment(self):
        """Set up isolated CI virtual environment."""
        self.log("Setting up isolated CI virtual environment...")
        
        venv_path = self.repo_root / self.venv_name
        
        if not venv_path.exists():
            self.log(f"Creating virtual environment: {venv_path}")
            self.run_command(["python", "-m", "venv", str(venv_path)])
        else:
            self.log("Virtual environment already exists")
        
        # Upgrade pip
        if self.is_windows:
            pip_cmd = [str(venv_path / "Scripts" / "pip.exe")]
        else:
            pip_cmd = [str(venv_path / "bin" / "pip")]
        
        self.run_command(pip_cmd + ["install", "-U", "pip"])
        
        # Install requirements
        if (self.repo_root / "requirements.txt").exists():
            self.run_command(pip_cmd + ["install", "-r", "requirements.txt"])
        
        if (self.repo_root / "requirements-dev.txt").exists():
            self.run_command(pip_cmd + ["install", "-r", "requirements-dev.txt"])
        
        # Install additional testing dependencies
        self.run_command(pip_cmd + ["install", "dnspython", "lxml"])
        
        self.log("Virtual environment setup complete")
    
    def clean_old_artifacts(self):
        """Clean old test and coverage artifacts."""
        self.log("Cleaning old artifacts...")
        
        patterns_to_clean = [
            ".coverage*",
            "*.pyc",
            "__pycache__",
            ".pytest_cache",
            "logs/nightly/*.xml",
            "logs/nightly/*.html",
            "logs/nightly/coverage_*"
        ]
        
        for pattern in patterns_to_clean:
            for path in self.repo_root.rglob(pattern):
                try:
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        shutil.rmtree(path)
                    self.log(f"Removed: {path}")
                except Exception as e:
                    self.log(f"Failed to remove {path}: {e}", "WARNING")
    
    def run_first_pass_tests(self):
        """Run first pass of tests with coverage."""
        self.log("Running first pass of tests...")
        
        # Run tests excluding slow/e2e/integration
        junit_file = self.logs_dir / "junit_first.xml"
        
        result = self.run_command([
            "python", "-m", "coverage", "run", "-m", "pytest", 
            "-q", "-k", "not slow and not e2e and not integration",
            f"--junitxml={junit_file}"
        ], check=False)
        
        # Generate coverage report
        coverage_file = self.logs_dir / "coverage_first_pass.txt"
        self.run_command([
            "python", "-m", "coverage", "report", "--show-missing"
        ], check=False)
        
        with open(coverage_file, "w") as f:
            report_result = self.run_command([
                "python", "-m", "coverage", "report", "--show-missing"
            ], check=False)
            f.write(report_result.stdout)
        
        self.log("First pass tests complete")
        return result.returncode == 0
    
    def generate_auto_smoke_tests(self):
        """Generate auto-smoke tests for coverage gaps."""
        self.log("Generating auto-smoke tests...")
        
        # Use the smoke test generator we created
        generator_script = self.repo_root / "tools" / "generate_auto_smoke_tests.py"
        if generator_script.exists():
            result = self.run_command([
                "python", str(generator_script)
            ], check=False)
            
            if result.returncode == 0:
                self.log("Auto-smoke tests generated successfully")
            else:
                self.log("Failed to generate auto-smoke tests", "WARNING")
        else:
            self.log("Smoke test generator not found", "WARNING")
    
    def run_second_pass_tests(self):
        """Run second pass with smoke tests."""
        self.log("Running second pass with smoke tests...")
        
        junit_file = self.logs_dir / "junit_second.xml"
        
        result = self.run_command([
            "python", "-m", "coverage", "run", "-m", "pytest",
            f"--junitxml={junit_file}"
        ], check=False)
        
        # Generate final coverage reports
        self.run_command([
            "python", "-m", "coverage", "html", 
            "-d", str(self.logs_dir / "coverage_final_html")
        ], check=False)
        
        coverage_final = self.logs_dir / "coverage_final.txt"
        with open(coverage_final, "w") as f:
            report_result = self.run_command([
                "python", "-m", "coverage", "report", "--show-missing"
            ], check=False)
            f.write(report_result.stdout)
        
        self.log("Second pass tests complete")
        return result.returncode == 0
    
    def run_security_audit(self):
        """Run security audit with bandit."""
        self.log("Running security audit...")
        
        security_file = self.logs_dir / "security_audit.json"
        
        result = self.run_command([
            "python", "-m", "bandit", "-r", "src/", "universal_recon/",
            "-f", "json", "-o", str(security_file)
        ], check=False)
        
        # Also generate text report
        security_txt = self.logs_dir / "security_audit.txt"
        text_result = self.run_command([
            "python", "-m", "bandit", "-r", "src/", "universal_recon/",
            "-f", "txt"
        ], check=False)
        
        with open(security_txt, "w") as f:
            f.write(text_result.stdout)
        
        self.log("Security audit complete")
    
    def generate_summary_report(self):
        """Generate comprehensive summary report."""
        self.log("Generating summary report...")
        
        summary_file = self.logs_dir / f"overnight_sprint_summary_{self.timestamp}.md"
        
        # Collect test results
        junit_files = list(self.logs_dir.glob("junit_*.xml"))
        coverage_files = list(self.logs_dir.glob("coverage_*.txt"))
        
        # Generate summary
        with open(summary_file, "w") as f:
            f.write(f"# Overnight Sprint v2 Summary Report\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Platform:** {platform.system()} {platform.release()}\n")
            f.write(f"**Python:** {sys.version}\n\n")
            
            f.write("## Test Results\n\n")
            f.write(f"- JUnit files generated: {len(junit_files)}\n")
            for junit_file in junit_files:
                f.write(f"  - {junit_file.name}\n")
            
            f.write("\n## Coverage Analysis\n\n")
            f.write(f"- Coverage reports generated: {len(coverage_files)}\n")
            for coverage_file in coverage_files:
                f.write(f"  - {coverage_file.name}\n")
            
            # Read final coverage if available
            final_coverage = self.logs_dir / "coverage_final.txt"
            if final_coverage.exists():
                f.write("\n### Final Coverage Summary\n\n")
                f.write("```\n")
                with open(final_coverage) as cf:
                    lines = cf.readlines()
                    # Get the TOTAL line
                    for line in lines:
                        if "TOTAL" in line:
                            f.write(line)
                            break
                f.write("```\n\n")
            
            f.write("## Security Audit\n\n")
            security_json = self.logs_dir / "security_audit.json"
            if security_json.exists():
                try:
                    with open(security_json) as sf:
                        security_data = json.load(sf)
                        f.write(f"- Issues found: {len(security_data.get('results', []))}\n")
                        f.write(f"- High severity: {len([r for r in security_data.get('results', []) if r.get('issue_severity') == 'HIGH'])}\n")
                        f.write(f"- Medium severity: {len([r for r in security_data.get('results', []) if r.get('issue_severity') == 'MEDIUM'])}\n")
                        f.write(f"- Low severity: {len([r for r in security_data.get('results', []) if r.get('issue_severity') == 'LOW'])}\n")
                except Exception as e:
                    f.write(f"- Error reading security audit: {e}\n")
            
            f.write("\n## Smoke Tests\n\n")
            smoke_summary = self.logs_dir / "auto_smoke_tests_summary.txt"
            if smoke_summary.exists():
                f.write("Auto-generated smoke tests:\n\n")
                with open(smoke_summary) as ss:
                    f.write(ss.read())
            
            f.write("\n## Files Generated\n\n")
            log_files = list(self.logs_dir.iterdir())
            for log_file in sorted(log_files):
                if log_file.is_file():
                    size = log_file.stat().st_size
                    f.write(f"- {log_file.name} ({size} bytes)\n")
        
        self.log(f"Summary report generated: {summary_file}")
    
    def run_overnight_sprint(self):
        """Run the complete overnight sprint."""
        self.log("Starting Overnight Sprint v2")
        self.log(f"Platform: {platform.system()}")
        self.log(f"Working directory: {self.repo_root}")
        
        try:
            # Step 1: Setup environment
            self.setup_virtual_environment()
            
            # Step 2: Clean old artifacts
            self.clean_old_artifacts()
            
            # Step 3: First pass tests
            self.run_first_pass_tests()
            
            # Step 4: Generate smoke tests
            self.generate_auto_smoke_tests()
            
            # Step 5: Second pass tests
            self.run_second_pass_tests()
            
            # Step 6: Security audit
            self.run_security_audit()
            
            # Step 7: Generate summary
            self.generate_summary_report()
            
            self.log("Overnight Sprint v2 completed successfully!")
            
        except Exception as e:
            self.log(f"Overnight Sprint failed: {e}", "ERROR")
            raise


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Overnight Sprint v2 - Cross-platform")
    parser.add_argument("--repo-root", help="Repository root directory")
    args = parser.parse_args()
    
    sprint = OvernightSprintV2(args.repo_root)
    sprint.run_overnight_sprint()


if __name__ == "__main__":
    main()