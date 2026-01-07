"""
CI-safe smoke tests for Google Sheets optional integration.

These tests verify that:
1. Importing the gsheets modules does NOT crash when dependencies are missing
2. The is_gsheets_available() function returns a boolean
3. The GSheetsNotInstalledError is raised when calling functions without deps

These tests run in CI without installing the [gsheets] extra.
"""

import pytest


class TestGSheetsExporter:
    """Tests for tools/gsheets_exporter.py"""

    def test_import_does_not_crash(self):
        """Importing gsheets_exporter should never crash, even without deps."""
        # This should not raise ImportError
        from tools import gsheets_exporter

        assert gsheets_exporter is not None

    def test_is_gsheets_available_returns_bool(self):
        """is_gsheets_available() should return a boolean."""
        from tools.gsheets_exporter import is_gsheets_available

        result = is_gsheets_available()
        assert isinstance(result, bool)

    def test_gsheets_not_installed_error_exists(self):
        """GSheetsNotInstalledError class should be importable."""
        from tools.gsheets_exporter import GSheetsNotInstalledError

        assert issubclass(GSheetsNotInstalledError, ImportError)

    def test_get_client_raises_friendly_error_when_unavailable(self):
        """get_client() should raise GSheetsNotInstalledError if deps missing."""
        from tools.gsheets_exporter import (
            GSheetsNotInstalledError,
            get_client,
            is_gsheets_available,
        )

        if not is_gsheets_available():
            with pytest.raises(GSheetsNotInstalledError) as exc_info:
                get_client()
            # Check friendly error message
            assert "pip install" in str(exc_info.value)
        else:
            # If deps are installed, we can't test this path
            pytest.skip("Google Sheets deps are installed; skipping unavailable test")


class TestGSheetsUtils:
    """Tests for universal_recon/plugins/google_sheets_utils.py"""

    def test_import_does_not_crash(self):
        """Importing google_sheets_utils should never crash, even without deps."""
        from universal_recon.plugins import google_sheets_utils

        assert google_sheets_utils is not None

    def test_is_gsheets_available_returns_bool(self):
        """is_gsheets_available() should return a boolean."""
        from universal_recon.plugins.google_sheets_utils import is_gsheets_available

        result = is_gsheets_available()
        assert isinstance(result, bool)

    def test_gsheets_not_installed_error_exists(self):
        """GSheetsNotInstalledError class should be importable."""
        from universal_recon.plugins.google_sheets_utils import GSheetsNotInstalledError

        assert issubclass(GSheetsNotInstalledError, ImportError)

    def test_export_returns_false_when_unavailable(self):
        """export_to_google_sheets() should return False gracefully if deps missing."""
        from universal_recon.plugins.google_sheets_utils import (
            export_to_google_sheets,
            is_gsheets_available,
        )

        if not is_gsheets_available():
            result = export_to_google_sheets(
                data=[{"name": "test"}],
                sheet_id="fake-sheet-id"
            )
            assert result is False
        else:
            pytest.skip("Google Sheets deps are installed; skipping unavailable test")


class TestPyprojectOptionalDeps:
    """Verify pyproject.toml has gsheets optional dependency."""

    def test_gsheets_extra_defined(self):
        """pyproject.toml should define [gsheets] optional dependency."""
        import tomllib
        from pathlib import Path

        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        assert pyproject_path.exists(), "pyproject.toml not found"

        with open(pyproject_path, "rb") as f:
            config = tomllib.load(f)

        optional_deps = config.get("project", {}).get("optional-dependencies", {})
        assert "gsheets" in optional_deps, "gsheets extra not defined in pyproject.toml"

        gsheets_deps = optional_deps["gsheets"]
        assert any("google-api-python-client" in dep for dep in gsheets_deps)
        assert any("gspread" in dep for dep in gsheets_deps)
