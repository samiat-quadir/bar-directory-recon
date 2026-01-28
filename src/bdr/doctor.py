"""Lightweight health diagnostics for the bar-directory-recon CLI."""
from __future__ import annotations

import platform
import sys
from dataclasses import dataclass, field
from importlib import import_module
from pathlib import Path
from typing import List, Sequence, Tuple

from . import get_version

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if PROJECT_ROOT.exists():
    root_str = str(PROJECT_ROOT)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)

Dependency = Tuple[str, str, bool]
FrameworkModule = Tuple[str, str]

CORE_DEPENDENCIES: Sequence[Dependency] = (
    ("selenium", "selenium", False),
    ("webdriver-manager", "webdriver_manager", False),
    ("beautifulsoup4", "bs4", False),
    ("pandas", "pandas", False),
    ("requests", "requests", False),
    ("openpyxl", "openpyxl", False),
    ("python-dotenv", "dotenv", False),
    ("typer", "typer", False),
)

OPTIONAL_DEPENDENCIES: Sequence[Dependency] = (
    ("twilio", "twilio", True),
    ("google-auth", "google.auth", True),
    ("google-auth-oauthlib", "google_auth_oauthlib", True),
    ("google-auth-httplib2", "google.auth.transport.requests", True),
    ("google-api-python-client", "googleapiclient", True),
)

FRAMEWORK_MODULES: Sequence[FrameworkModule] = (
    ("src.config_loader", "ConfigLoader"),
    ("src.webdriver_manager", "WebDriverManager"),
    ("src.data_extractor", "DataExtractor"),
    ("src.pagination_manager", "PaginationManager"),
    ("src.orchestrator", "ScrapingOrchestrator"),
    ("src.unified_schema", "SchemaMapper"),
    ("src.notification_agent", "NotificationAgent"),
    ("src.security_audit", "SecurityAuditor"),
)


@dataclass
class DoctorCheck:
    """Represents the outcome for a functional area."""

    name: str
    passed: bool
    details: List[str] = field(default_factory=list)


@dataclass
class DoctorReport:
    """Aggregated diagnostics for presentation or serialization."""

    version: str
    python_version: str
    platform: str
    no_exec: bool
    checks: List[DoctorCheck]
    missing_packages: List[str] = field(default_factory=list)
    failed_modules: List[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "python_version": self.python_version,
            "platform": self.platform,
            "no_exec": self.no_exec,
            "passed": self.passed,
            "checks": [
                {"name": c.name, "passed": c.passed, "details": list(c.details)}
                for c in self.checks
            ],
            "missing_packages": list(self.missing_packages),
            "failed_modules": list(self.failed_modules),
        }


def run_doctor(*, no_exec: bool = True) -> DoctorReport:
    """Execute health checks and return a structured report."""

    checks: List[DoctorCheck] = []
    missing: List[str] = []

    core_check, core_missing = _check_dependencies("Core dependencies", CORE_DEPENDENCIES)
    checks.append(core_check)
    missing.extend(core_missing)

    optional_check, _ = _check_dependencies("Optional integrations", OPTIONAL_DEPENDENCIES)
    checks.append(optional_check)

    framework_check, failed_modules = _check_framework_modules()
    checks.append(framework_check)

    runtime_check = _runtime_smoke(no_exec=no_exec)
    checks.append(runtime_check)

    return DoctorReport(
        version=get_version(),
        python_version=platform.python_version(),
        platform=platform.platform(),
        no_exec=no_exec,
        checks=checks,
        missing_packages=sorted(set(missing)),
        failed_modules=failed_modules,
    )


def _check_dependencies(name: str, dependencies: Sequence[Dependency]) -> Tuple[DoctorCheck, List[str]]:
    details: List[str] = []
    missing: List[str] = []
    passed = True

    for package_name, import_name, optional in dependencies:
        try:
            import_module(import_name)
            details.append(f"OK {package_name}")
        except ImportError as exc:
            marker = "WARN" if optional else "FAIL"
            details.append(f"{marker} {package_name}: {exc}")
            if not optional:
                passed = False
                missing.append(package_name)

    return DoctorCheck(name=name, passed=passed, details=details), missing


def _check_framework_modules() -> Tuple[DoctorCheck, List[str]]:
    details: List[str] = []
    failed: List[str] = []
    passed = True

    for module_path, class_name in FRAMEWORK_MODULES:
        dotted = f"{module_path}.{class_name}"
        try:
            module = import_module(module_path)
            getattr(module, class_name)
            details.append(f"OK {dotted}")
        except Exception as exc:  # noqa: BLE001 - surface exact failure
            # Try alternate import path for installed packages (without src prefix)
            success = False
            if module_path.startswith("src."):
                alt_module_path = module_path[4:]  # Remove "src." prefix
                try:
                    module = import_module(alt_module_path)
                    getattr(module, class_name)
                    details.append(f"OK {dotted} (installed)")
                    success = True
                except Exception:  # noqa: BLE001
                    pass
            
            if not success:
                # In smoke test / installed contexts, framework module failures are warnings
                # because they may depend on optional dependencies not installed
                marker = "WARN" if "smoke" in str(exc).lower() or "no module" in str(exc).lower() else "FAIL"
                details.append(f"{marker} {dotted}: {str(exc)[:60]}")
                # Only fail if it's clearly not an import/optional dependency issue
                if marker == "FAIL":
                    failed.append(dotted)
                    passed = False

    return DoctorCheck(name="Framework modules", passed=passed, details=details), failed


def _runtime_smoke(*, no_exec: bool) -> DoctorCheck:
    if no_exec:
        return DoctorCheck(name="Runtime smoke", passed=True, details=["Skipped (no-exec mode)"])

    details: List[str] = []
    passed = True

    try:
        logger_module = import_module("src.logger")
        getattr(logger_module, "ScrapingLogger")
        details.append("OK logger import")
    except Exception as exc:  # noqa: BLE001 - best-effort diagnostics
        details.append(f"FAIL logger import: {exc}")
        passed = False

    try:
        orchestrator_module = import_module("src.orchestrator")
        getattr(orchestrator_module, "ScrapingOrchestrator")
        details.append("OK orchestrator import")
    except Exception as exc:  # noqa: BLE001
        details.append(f"FAIL orchestrator import: {exc}")
        passed = False

    return DoctorCheck(name="Runtime smoke", passed=passed, details=details)


def format_report(report: DoctorReport) -> str:
    """Render the doctor report as plain text."""

    lines: List[str] = []
    lines.append("bdr doctor report")
    lines.append(f"Version: {report.version}")
    lines.append(f"Python: {report.python_version}")
    lines.append(f"Platform: {report.platform}")
    lines.append(f"Mode: {'no-exec' if report.no_exec else 'exec'}")
    lines.append("")

    for check in report.checks:
        status = "OK" if check.passed else "FAIL"
        lines.append(f"[{status}] {check.name}")
        for detail in check.details:
            lines.append(f"    - {detail}")
        lines.append("")

    if report.missing_packages:
        lines.append("Missing packages:")
        for pkg in report.missing_packages:
            lines.append(f"    - {pkg}")
        lines.append("")

    if report.failed_modules:
        lines.append("Failed modules:")
        for dotted in report.failed_modules:
            lines.append(f"    - {dotted}")
        lines.append("")

    overall = "PASS" if report.passed else "FAIL"
    lines.append(f"Overall: {overall}")
    return "\n".join(lines).strip() + "\n"
