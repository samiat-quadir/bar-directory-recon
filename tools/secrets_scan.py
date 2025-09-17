#!/usr/bin/env python3
"""
Secrets Scan Utility

This script scans directories and files for potential secrets/sensitive information
such as API keys, passwords, and credentials. It can be configured with custom
patterns and includes functionality to:

1. Scan specific file types
2. Ignore directories (like node_modules, .git)
3. Generate a JSON report of findings
4. Suggest remediation steps

Usage:
    python secrets_scan.py --path /path/to/scan --report-path /path/for/report

Author: GitHub Copilot
Created: May 2025
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime

# Default configuration
DEFAULT_CONFIG = {
    "file_extensions": [
        ".env",
        ".ini",
        ".config",
        ".xml",
        ".json",
        ".yaml",
        ".yml",
        ".py",
        ".js",
        ".ps1",
        ".sh",
        ".bat",
        ".cmd",
        ".txt",
        ".md",
        ".cs",
        ".java",
        ".html",
        ".htm",
        ".css",
        ".sql",
    ],
    "exclude_dirs": [
        ".git",
        ".venv",
        "venv",
        "env",
        "node_modules",
        "__pycache__",
        "bin",
        "obj",
        "dist",
        "build",
    ],
    "exclude_files": ["package-lock.json", "yarn.lock", "poetry.lock"],
    "patterns": [
        {
            "name": "API Key",
            "regex": r"(?i)(api[-_]?key|apikey|api[-_]?token)(?:=|:|,|\s|'|\")([a-zA-Z0-9_\-]{10,})(?:'|\"|,|\s|$)",
            "severity": "HIGH",
        },
        {
            "name": "AWS Access Key",
            "regex": r"(?i)aws(?:_|-)?(?:access(?:_|-)?)?key(?:_|-)?id(?:=|:|,|\s|'|\")([A-Z0-9]{20})(?:'|\"|,|\s|$)",
            "severity": "HIGH",
        },
        {
            "name": "AWS Secret Key",
            "regex": r"(?i)aws(?:_|-)?secret(?:_|-)?(?:access(?:_|-)?)?key(?:=|:|,|\s|'|\")([A-Za-z0-9/+=]{40})(?:'|\"|,|\s|$)",
            "severity": "HIGH",
        },
        {
            "name": "Password",
            "regex": r"(?i)(password|passwd|pwd)(?:=|:|,|\s|'|\")(?!.*(?:\$\{|\$\(|\{\{|\$env:))(.{8,})(?:'|\"|,|\s|$)",
            "severity": "MEDIUM",
        },
        {
            "name": "Database Connection String",
            "regex": r"(?i)((?:connection(?:_|-)?string|conn(?:_|-)?str)(?:=|:|,|\s|'|\").*(?:Server|Host|Database|Uid|Pwd).*(?:'|\"|,|\s|$))",
            "severity": "HIGH",
        },
        {
            "name": "Generic Secret",
            "regex": r"(?i)(secret|private[-_]?key)(?:=|:|,|\s|'|\")(.{8,})(?:'|\"|,|\s|$)",
            "severity": "MEDIUM",
        },
        {
            "name": "JWT Token",
            "regex": r"(?i)(jwt|token|bearer)(?:=|:|,|\s|'|\")([a-zA-Z0-9_=]+\.[a-zA-Z0-9_=]+\.[a-zA-Z0-9_\-\+/=]*)(?:'|\"|,|\s|$)",
            "severity": "MEDIUM",
        },
        {
            "name": "SSH Private Key",
            "regex": r"-----BEGIN (?:RSA|DSA|EC|OPENSSH) PRIVATE KEY-----",
            "severity": "HIGH",
        },
        {
            "name": "GitHub Token",
            "regex": r"(?i)github[_\-\s]*(token|key|secret)[ :='\"]+((?:ghp|gho|ghu|ghs|ghr|github_pat)_[a-zA-Z0-9_]{36,255})",
            "severity": "HIGH",
        },
        {
            "name": "Google API Key",
            "regex": r"(?i)(google|firebase|google[-_]?cloud|gcp)[-_]?(key|token|secret)[ :='\"]+(AIza[a-zA-Z0-9_\-]{35})",
            "severity": "HIGH",
        },
    ],
}


class SecretsScanner:
    """Class that handles secrets scanning functionality."""

    def __init__(self, config=None):
        """Initialize the scanner with the given configuration."""
        self.config = config or DEFAULT_CONFIG
        self.findings = []
        self.start_time = None
        self.end_time = None
        self.files_scanned = 0
        self.files_with_secrets = 0

    def should_scan_file(self, filepath):
        """Determine if a file should be scanned based on extension and exclusion rules."""
        # Check if file is in excluded list
        filename = os.path.basename(filepath)
        if filename in self.config["exclude_files"]:
            return False

        # Check file extension
        _, ext = os.path.splitext(filepath)
        return ext in self.config["file_extensions"]

    def should_scan_dir(self, dirpath):
        """Determine if a directory should be scanned based on exclusion rules."""
        dirname = os.path.basename(dirpath)
        return dirname not in self.config["exclude_dirs"]

    def scan_file(self, filepath):
        """Scan a single file for secrets."""
        self.files_scanned += 1

        try:
            with open(filepath, encoding="utf-8", errors="ignore") as file:
                line_number = 0
                file_findings = []

                for line in file:
                    line_number += 1
                    line = line.rstrip()

                    for pattern in self.config["patterns"]:
                        matches = re.finditer(pattern["regex"], line)
                        for match in matches:
                            # Get the matched text
                            matched_text = match.group(0)

                            # Get the secret value when possible (from a capturing group)
                            secret_value = None
                            if len(match.groups()) > 0:
                                for group in match.groups():
                                    if (
                                        group and len(group) > 4
                                    ):  # Only consider groups that look like they could be secrets
                                        secret_value = group
                                        break

                            # If no good group was found, use the full match
                            if not secret_value:
                                secret_value = matched_text

                            # Create a redacted line for the report
                            redacted_line = re.sub(
                                re.escape(secret_value), "[REDACTED]", line
                            )

                            # Add the finding
                            file_findings.append(
                                {
                                    "line_number": line_number,
                                    "pattern_name": pattern["name"],
                                    "severity": pattern["severity"],
                                    "redacted_line": redacted_line,
                                }
                            )

                if file_findings:
                    self.files_with_secrets += 1
                    self.findings.append(
                        {
                            "file_path": filepath,
                            "relative_path": os.path.relpath(filepath, os.getcwd()),
                            "secret_count": len(file_findings),
                            "findings": file_findings,
                        }
                    )

        except Exception as e:
            print(f"Error scanning file {filepath}: {str(e)}")

    def scan_directory(self, directory):
        """Recursively scan a directory for secrets."""
        try:
            for root, dirs, files in os.walk(directory):
                # Filter directories
                dirs[:] = [
                    d for d in dirs if self.should_scan_dir(os.path.join(root, d))
                ]

                # Scan each file
                for file in files:
                    filepath = os.path.join(root, file)
                    if self.should_scan_file(filepath):
                        self.scan_file(filepath)

        except Exception as e:
            print(f"Error scanning directory {directory}: {str(e)}")

    def start_scan(self, path):
        """Start the scanning process on the given path."""
        self.start_time = datetime.now()
        print(f"Starting scan at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Scanning path: {path}")

        if os.path.isfile(path):
            if self.should_scan_file(path):
                self.scan_file(path)
            else:
                print(f"Skipping file {path} (excluded by configuration)")
        elif os.path.isdir(path):
            self.scan_directory(path)
        else:
            print(f"Error: Path {path} does not exist")

        self.end_time = datetime.now()
        scan_duration = (self.end_time - self.start_time).total_seconds()

        print(f"\nScan completed in {scan_duration:.2f} seconds")
        print(f"Files scanned: {self.files_scanned}")
        print(f"Files with secrets: {self.files_with_secrets}")
        print(f"Total secrets found: {sum(f['secret_count'] for f in self.findings)}")

    def generate_report(self, report_path=None):
        """Generate a JSON report of the findings."""
        report = {
            "scan_info": {
                "start_time": (
                    self.start_time.strftime("%Y-%m-%d %H:%M:%S")
                    if self.start_time
                    else None
                ),
                "end_time": (
                    self.end_time.strftime("%Y-%m-%d %H:%M:%S")
                    if self.end_time
                    else None
                ),
                "files_scanned": self.files_scanned,
                "files_with_secrets": self.files_with_secrets,
                "total_secrets": sum(f["secret_count"] for f in self.findings),
            },
            "findings": self.findings,
            "remediation_suggestions": [
                "Store secrets in environment variables or a secrets manager",
                "Use configuration files that are not checked into source control",
                "Consider using Azure Key Vault, AWS Secrets Manager, or similar services",
                "For local development, use a .env file that is in your .gitignore",
                "For CI/CD, use the secrets management feature of your CI/CD platform",
            ],
        }

        if report_path:
            try:
                os.makedirs(os.path.dirname(report_path), exist_ok=True)
                with open(report_path, "w", encoding="utf-8") as f:
                    json.dump(report, f, indent=2)
                print(f"Report saved to {report_path}")
            except Exception as e:
                print(f"Error saving report to {report_path}: {str(e)}")

        return report


def main():
    parser = argparse.ArgumentParser(
        description="Scan for secrets and sensitive information in files"
    )
    parser.add_argument(
        "--path", default=os.getcwd(), help="Path to scan (file or directory)"
    )
    parser.add_argument("--report-path", help="Path to save the JSON report")
    parser.add_argument("--config", help="Path to custom configuration JSON file")

    args = parser.parse_args()

    # Load custom configuration if provided
    config = DEFAULT_CONFIG
    if args.config:
        try:
            with open(args.config, encoding="utf-8") as f:
                custom_config = json.load(f)
                config.update(custom_config)
        except Exception as e:
            print(f"Error loading custom configuration: {str(e)}")
            sys.exit(1)

    # Create scanner and run scan
    scanner = SecretsScanner(config)
    scanner.start_scan(args.path)

    # Generate report
    if args.report_path:
        report_path = args.report_path
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(os.getcwd(), f"secrets_scan_report_{timestamp}.json")

    scanner.generate_report(report_path)

    # Return non-zero exit code if secrets were found (useful for CI/CD)
    if scanner.findings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
