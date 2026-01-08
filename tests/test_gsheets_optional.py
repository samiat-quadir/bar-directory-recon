"""
CI-safe smoke tests for Google Sheets optional integration.

These tests verify that:
1. Importing the gsheets modules does NOT crash when dependencies are missing
2. The is_gsheets_available() function returns a boolean
3. The GSheetsNotInstalledError is raised when calling functions without deps
4. CLI entrypoint works (--help, --check, arg parsing)

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


class TestGSheetsExporterCLI:
    """Tests for gsheets_exporter CLI entrypoint (no network calls)."""

    def test_help_flag_shows_usage(self, capsys):
        """--help should print usage information and exit cleanly."""
        from tools.gsheets_exporter import main

        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])

        # argparse exits with 0 for --help
        assert exc_info.value.code == 0

        captured = capsys.readouterr()
        # Should contain key usage elements
        assert "gsheets_exporter" in captured.out
        assert "--demo" in captured.out
        assert "--check" in captured.out

    def test_check_flag_returns_correct_status(self, capsys):
        """--check should report dependency status without network calls."""
        from tools.gsheets_exporter import is_gsheets_available, main

        exit_code = main(["--check"])

        captured = capsys.readouterr()
        if is_gsheets_available():
            assert exit_code == 0
            assert "installed" in captured.out.lower()
        else:
            assert exit_code == 1
            assert "not installed" in captured.out.lower()
            assert "pip install" in captured.out

    def test_demo_dry_run_no_network(self, capsys):
        """--demo --dry-run should work without network or credentials."""
        from tools.gsheets_exporter import main

        exit_code = main(["--demo", "--dry-run"])

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Dry run" in captured.out
        assert "timestamp" in captured.out

    def test_demo_without_creds_returns_error(self, capsys, monkeypatch):
        """--demo without credentials should return friendly error."""
        from tools.gsheets_exporter import main

        # Clear env vars
        monkeypatch.delenv("GOOGLE_SHEETS_CREDENTIALS_PATH", raising=False)
        monkeypatch.delenv("GOOGLE_SA_JSON", raising=False)

        exit_code = main(["--demo"])

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "GOOGLE_SHEETS_CREDENTIALS_PATH" in captured.out

    def test_invalid_json_data_returns_error(self, capsys):
        """--data with invalid JSON should return friendly error."""
        from tools.gsheets_exporter import main

        exit_code = main(["--data", "not valid json"])

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Invalid JSON" in captured.out

    def test_no_args_shows_help(self, capsys):
        """No arguments should show help (no error)."""
        from tools.gsheets_exporter import main

        exit_code = main([])

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "--help" in captured.out or "usage" in captured.out.lower()

    def test_gsheets_not_installed_error_message(self):
        """GSheetsNotInstalledError should have install instructions."""
        from tools.gsheets_exporter import GSheetsNotInstalledError

        error = GSheetsNotInstalledError()
        msg = str(error)

        assert "pip install" in msg
        assert "gsheets" in msg.lower()


class TestWorksheetNotFoundError:
    """Tests for WorksheetNotFoundError UX improvements."""

    def test_worksheet_not_found_error_contains_available_list(self):
        """WorksheetNotFoundError should list available worksheets."""
        from tools.gsheets_exporter import WorksheetNotFoundError

        error = WorksheetNotFoundError(
            worksheet_name="NonExistent",
            available_worksheets=["Sheet1", "Data", "Results"],
            spreadsheet_id="test-id"
        )
        msg = str(error)

        assert "NonExistent" in msg
        assert "not found" in msg.lower()
        assert "Sheet1" in msg
        assert "Data" in msg
        assert "Results" in msg
        assert "--worksheet" in msg

    def test_worksheet_not_found_error_suggests_first_available(self):
        """WorksheetNotFoundError should suggest first available worksheet."""
        from tools.gsheets_exporter import WorksheetNotFoundError

        error = WorksheetNotFoundError(
            worksheet_name="BadName",
            available_worksheets=["FirstSheet", "SecondSheet"],
            spreadsheet_id="test-id"
        )
        msg = str(error)

        # Should suggest using the first available
        assert "FirstSheet" in msg

    def test_worksheet_not_found_error_handles_empty_list(self):
        """WorksheetNotFoundError should handle empty worksheet list gracefully."""
        from tools.gsheets_exporter import WorksheetNotFoundError

        error = WorksheetNotFoundError(
            worksheet_name="Test",
            available_worksheets=[],
            spreadsheet_id="test-id"
        )
        msg = str(error)

        assert "Test" in msg
        assert "not found" in msg.lower()

    def test_worksheet_not_found_is_value_error(self):
        """WorksheetNotFoundError should be a ValueError subclass."""
        from tools.gsheets_exporter import WorksheetNotFoundError

        assert issubclass(WorksheetNotFoundError, ValueError)


class TestWorksheetFallbackBehavior:
    """Tests for worksheet fallback and listing behavior (mocked, no network)."""

    def test_list_worksheets_function_exists(self):
        """list_worksheets function should be importable."""
        from tools.gsheets_exporter import list_worksheets

        assert callable(list_worksheets)

    def test_get_worksheet_with_fallback_helper_exists(self):
        """_get_worksheet_with_fallback helper should be importable."""
        from tools.gsheets_exporter import _get_worksheet_with_fallback

        assert callable(_get_worksheet_with_fallback)

    def test_export_rows_accepts_fallback_param(self):
        """export_rows should accept fallback_to_first parameter."""
        import inspect

        from tools.gsheets_exporter import export_rows

        sig = inspect.signature(export_rows)
        params = list(sig.parameters.keys())

        assert "fallback_to_first" in params

    def test_cli_has_fallback_option(self, capsys):
        """CLI should have --fallback option."""
        from tools.gsheets_exporter import main

        with pytest.raises(SystemExit):
            main(["--help"])

        captured = capsys.readouterr()
        assert "--fallback" in captured.out

    def test_cli_has_list_worksheets_option(self, capsys):
        """CLI should have --list-worksheets option."""
        from tools.gsheets_exporter import main

        with pytest.raises(SystemExit):
            main(["--help"])

        captured = capsys.readouterr()
        assert "--list-worksheets" in captured.out
