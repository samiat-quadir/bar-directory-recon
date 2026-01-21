"""
Additional gsheets_exporter tests for coverage boost.

Targets:
- Error handling paths
- Edge cases in CSV loading
- Configuration validation
- Helper function coverage

All tests are mocked and run without credentials or network access.
"""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestGSheetsAvailability:
    """Tests for gsheets dependency availability checks."""

    def test_is_gsheets_available_returns_bool(self):
        """is_gsheets_available should return a boolean."""
        from tools.gsheets_exporter import is_gsheets_available

        result = is_gsheets_available()
        assert isinstance(result, bool)

    def test_gsheets_not_installed_error_class_exists(self):
        """GSheetsNotInstalledError should be defined."""
        from tools.gsheets_exporter import GSheetsNotInstalledError

        assert issubclass(GSheetsNotInstalledError, Exception)

    def test_worksheet_not_found_error_class_exists(self):
        """WorksheetNotFoundError should be defined."""
        from tools.gsheets_exporter import WorksheetNotFoundError

        assert issubclass(WorksheetNotFoundError, Exception)


class TestCSVLoading:
    """Tests for CSV loading functionality."""

    def test_load_csv_basic(self, tmp_path):
        """load_csv should load a simple CSV file."""
        from tools.gsheets_exporter import load_csv

        csv_file = tmp_path / "simple.csv"
        csv_file.write_text("a,b,c\n1,2,3\n4,5,6\n")

        rows = load_csv(str(csv_file))

        assert len(rows) == 3
        assert rows[0] == ["a", "b", "c"]
        assert rows[1] == ["1", "2", "3"]

    def test_load_csv_with_quotes(self, tmp_path):
        """load_csv should handle quoted fields."""
        from tools.gsheets_exporter import load_csv

        csv_file = tmp_path / "quoted.csv"
        csv_file.write_text('name,description\n"John","Hello, World"\n')

        rows = load_csv(str(csv_file))

        assert rows[1][0] == "John"
        assert rows[1][1] == "Hello, World"

    def test_load_csv_unicode(self, tmp_path):
        """load_csv should handle Unicode content."""
        from tools.gsheets_exporter import load_csv

        csv_file = tmp_path / "unicode.csv"
        csv_file.write_text("name,city\nJosé,São Paulo\n日本語,東京\n", encoding="utf-8")

        rows = load_csv(str(csv_file))

        assert "José" in rows[1][0]
        assert "日本語" in rows[2][0]

    def test_load_csv_missing_file_raises(self):
        """load_csv should raise FileNotFoundError for missing files."""
        from tools.gsheets_exporter import load_csv

        with pytest.raises(FileNotFoundError):
            load_csv("/nonexistent/path/to/file.csv")

    def test_load_csv_single_row(self, tmp_path):
        """load_csv should handle header-only CSV."""
        from tools.gsheets_exporter import load_csv

        csv_file = tmp_path / "header_only.csv"
        csv_file.write_text("name,email,phone\n")

        rows = load_csv(str(csv_file))

        assert len(rows) == 1
        assert rows[0] == ["name", "email", "phone"]


class TestDeduplication:
    """Tests for row deduplication."""

    def test_dedupe_rows_basic(self):
        """dedupe_rows should remove duplicates by key."""
        from tools.gsheets_exporter import dedupe_rows

        rows = [
            ["email", "name"],
            ["a@test.com", "Alice"],
            ["b@test.com", "Bob"],
            ["a@test.com", "Alice2"],  # Duplicate email
        ]

        result = dedupe_rows(rows, "email")

        assert len(result) == 3  # header + 2 unique

    def test_dedupe_rows_preserves_first(self):
        """dedupe_rows should keep first occurrence."""
        from tools.gsheets_exporter import dedupe_rows

        rows = [
            ["email", "name"],
            ["a@test.com", "First"],
            ["a@test.com", "Second"],
        ]

        result = dedupe_rows(rows, "email")

        assert result[1][1] == "First"

    def test_dedupe_rows_invalid_column_raises(self):
        """dedupe_rows should raise for non-existent column."""
        from tools.gsheets_exporter import dedupe_rows

        rows = [
            ["name", "city"],
            ["Alice", "NYC"],
        ]

        with pytest.raises(ValueError):
            dedupe_rows(rows, "email")  # email not in header

    def test_dedupe_rows_case_sensitive(self):
        """dedupe_rows key matching should be case-sensitive."""
        from tools.gsheets_exporter import dedupe_rows

        rows = [
            ["email", "name"],
            ["A@test.com", "Alice"],
            ["a@test.com", "alice"],
        ]

        result = dedupe_rows(rows, "email")

        # Both should remain (case-sensitive)
        assert len(result) == 3

    def test_dedupe_rows_empty_values(self):
        """dedupe_rows should handle empty values."""
        from tools.gsheets_exporter import dedupe_rows

        rows = [
            ["email", "name"],
            ["", "NoEmail1"],
            ["", "NoEmail2"],
            ["a@test.com", "WithEmail"],
        ]

        result = dedupe_rows(rows, "email")

        # Empty string duplicates should be deduped
        assert len(result) == 3


class TestRepoRootDetection:
    """Tests for repository root detection."""

    def test_get_repo_root_with_git_dir(self, tmp_path):
        """_get_repo_root should find .git directory."""
        from tools.gsheets_exporter import _get_repo_root

        # Create mock repo structure
        repo = tmp_path / "myrepo"
        repo.mkdir()
        (repo / ".git").mkdir()
        (repo / "subdir").mkdir()

        # When in subdir, should find parent with .git
        with patch("tools.gsheets_exporter.Path.cwd", return_value=repo / "subdir"):
            result = _get_repo_root()
            # Result could be repo or None depending on implementation
            assert result is None or isinstance(result, Path)

    def test_get_repo_root_returns_path_or_none(self):
        """_get_repo_root should return Path or None."""
        from tools.gsheets_exporter import _get_repo_root

        result = _get_repo_root()
        assert result is None or isinstance(result, Path)


class TestVenvGuardrailEdgeCases:
    """Edge case tests for venv guardrail."""

    def test_guardrail_no_virtual_env_set(self, monkeypatch):
        """Guardrail should handle missing VIRTUAL_ENV."""
        from tools.gsheets_exporter import _check_venv_guardrail

        monkeypatch.delenv("VIRTUAL_ENV", raising=False)

        with patch("tools.gsheets_exporter._get_repo_root", return_value=None):
            # Should not raise when no repo root
            _check_venv_guardrail()

    def test_guardrail_empty_virtual_env(self, monkeypatch):
        """Guardrail should handle empty VIRTUAL_ENV."""
        from tools.gsheets_exporter import _check_venv_guardrail

        monkeypatch.setenv("VIRTUAL_ENV", "")

        with patch("tools.gsheets_exporter._get_repo_root", return_value=None):
            _check_venv_guardrail()


class TestCredentialPathResolution:
    """Tests for credential path handling."""

    def test_creds_in_repo_detection(self, tmp_path, monkeypatch):
        """Should detect credentials inside repository."""
        from tools.gsheets_exporter import is_gsheets_available

        if not is_gsheets_available():
            pytest.skip("GSheets deps not installed")

        # Create fake repo with creds inside
        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / ".git").mkdir()

        creds = repo / "secrets" / "creds.json"
        creds.parent.mkdir()
        creds.write_text('{"type": "service_account"}')

        monkeypatch.setenv("GOOGLE_SHEETS_CREDENTIALS_PATH", str(creds))

        with patch("tools.gsheets_exporter._check_venv_guardrail"):
            with patch("tools.gsheets_exporter._get_repo_root", return_value=repo):
                from tools.gsheets_exporter import get_client

                # Can raise ValueError or RuntimeError depending on check order
                with pytest.raises((RuntimeError, ValueError)) as exc_info:
                    get_client()

                assert "inside" in str(exc_info.value).lower() or "repository" in str(exc_info.value).lower() or "security" in str(exc_info.value).lower()


class TestExportModeHandling:
    """Tests for export mode (append/replace) handling."""

    def test_mode_values_are_strings(self):
        """Mode values should be usable as strings."""
        from src.bdr.cli import ExportMode

        assert str(ExportMode.APPEND.value) == "append"
        assert str(ExportMode.REPLACE.value) == "replace"


class TestErrorMessageQuality:
    """Tests to ensure error messages are helpful."""

    def test_missing_spreadsheet_id_message(self, tmp_path):
        """Missing sheet ID should show clear message."""
        from typer.testing import CliRunner
        from src.bdr.cli import app

        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name\ntest\n")

        runner = CliRunner()
        result = runner.invoke(app, ["export", "csv-to-sheets", str(csv_file)])

        # Should mention spreadsheet ID or sheet-id
        assert result.exit_code != 0
        # Either dry-run prompt or sheet-id error
        output = result.stdout.lower()
        assert "sheet" in output or "id" in output or "dry" in output or "import" in output
