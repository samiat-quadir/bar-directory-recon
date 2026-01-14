"""
Tests for the Golden Path: CSV → Google Sheets export workflow.

These tests verify:
1. The CLI `bdr export csv-to-sheets` command works as documented
2. The venv interpreter guardrail functions correctly
3. Credential error messages are clear and actionable
4. CSV loading, deduplication, and export work without network calls

All tests are mocked and run without credentials or network access.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestVenvGuardrail:
    """Tests for interpreter/venv guardrail."""

    def test_check_venv_guardrail_function_exists(self):
        """_check_venv_guardrail should be importable."""
        from tools.gsheets_exporter import _check_venv_guardrail

        assert callable(_check_venv_guardrail)

    def test_check_venv_guardrail_passes_when_in_venv(self, monkeypatch, tmp_path):
        """Guardrail should pass when running inside project venv."""
        from tools.gsheets_exporter import _check_venv_guardrail

        # Simulate being in a project venv
        repo_root = tmp_path / "project"
        repo_root.mkdir()
        (repo_root / ".git").mkdir()

        venv_path = repo_root / ".venv"
        venv_path.mkdir()

        # Set VIRTUAL_ENV to point to project venv
        monkeypatch.setenv("VIRTUAL_ENV", str(venv_path))

        # Patch _get_repo_root to return our test repo
        with patch("tools.gsheets_exporter._get_repo_root", return_value=repo_root):
            # Should not raise
            _check_venv_guardrail()

    def test_check_venv_guardrail_skips_when_no_repo(self):
        """Guardrail should skip check when not in a git repo."""
        from tools.gsheets_exporter import _check_venv_guardrail

        with patch("tools.gsheets_exporter._get_repo_root", return_value=None):
            # Should not raise even without venv
            _check_venv_guardrail()


class TestCredentialMessages:
    """Tests for clear credential error messages."""

    def test_missing_creds_error_shows_instructions(self, monkeypatch):
        """Missing credentials should show setup instructions."""
        from tools.gsheets_exporter import get_client, is_gsheets_available

        if not is_gsheets_available():
            pytest.skip("GSheets deps not installed")

        # Clear env vars
        monkeypatch.delenv("GOOGLE_SHEETS_CREDENTIALS_PATH", raising=False)
        monkeypatch.delenv("GOOGLE_SA_JSON", raising=False)

        # Skip venv check for this test
        with patch("tools.gsheets_exporter._check_venv_guardrail"):
            with pytest.raises(RuntimeError) as exc_info:
                get_client()

        msg = str(exc_info.value)
        # Should contain setup instructions
        assert "GOOGLE_SHEETS_CREDENTIALS_PATH" in msg
        assert "PowerShell" in msg or "export" in msg
        assert "OUTSIDE" in msg or "secrets" in msg.lower()

    def test_legacy_env_var_emits_deprecation_warning(self, monkeypatch, tmp_path):
        """Using GOOGLE_SA_JSON should emit deprecation warning."""
        from tools.gsheets_exporter import get_client, is_gsheets_available

        if not is_gsheets_available():
            pytest.skip("GSheets deps not installed")

        # Create fake credentials file outside "repo"
        creds_file = tmp_path / "sa.json"
        creds_file.write_text('{"type": "service_account"}')

        # Set legacy env var
        monkeypatch.delenv("GOOGLE_SHEETS_CREDENTIALS_PATH", raising=False)
        monkeypatch.setenv("GOOGLE_SA_JSON", str(creds_file))

        # Patch repo root to be different from tmp_path
        fake_repo = tmp_path / "repo"
        fake_repo.mkdir()

        with patch("tools.gsheets_exporter._check_venv_guardrail"):
            with patch("tools.gsheets_exporter._get_repo_root", return_value=fake_repo):
                with pytest.warns(DeprecationWarning) as warning_info:
                    try:
                        get_client()
                    except Exception:
                        pass  # May fail on actual auth, we just want the warning

        # Check deprecation warning was emitted
        assert len(warning_info) > 0
        assert any("GOOGLE_SA_JSON" in str(w.message) for w in warning_info)
        assert any("deprecated" in str(w.message).lower() for w in warning_info)


class TestGoldenPathCSVOperations:
    """Tests for CSV operations in the golden path."""

    def test_load_csv_handles_bom(self, tmp_path):
        """load_csv should handle UTF-8 BOM correctly."""
        from tools.gsheets_exporter import load_csv

        # Create CSV with BOM
        csv_file = tmp_path / "with_bom.csv"
        csv_file.write_bytes(b"\xef\xbb\xbfname,email\nJohn,john@example.com\n")

        rows = load_csv(str(csv_file))

        # First column header should NOT have BOM
        assert rows[0][0] == "name"

    def test_load_csv_empty_file_raises_error(self, tmp_path):
        """load_csv should raise ValueError for empty files."""
        from tools.gsheets_exporter import load_csv

        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")

        with pytest.raises(ValueError) as exc_info:
            load_csv(str(csv_file))

        assert "empty" in str(exc_info.value).lower()

    def test_dedupe_with_many_duplicates(self):
        """dedupe_rows should handle many duplicates efficiently."""
        from tools.gsheets_exporter import dedupe_rows

        # Create 1000 rows with 100 unique emails
        header = ["name", "email"]
        rows = [header]
        for i in range(1000):
            email = f"user{i % 100}@example.com"
            rows.append([f"User {i}", email])

        result = dedupe_rows(rows, "email")

        # Should have header + 100 unique
        assert len(result) == 101

    def test_export_csv_to_sheets_dry_run_flow(self, tmp_path, capsys):
        """Verify dry-run flow for CSV export."""
        from tools.gsheets_exporter import load_csv, dedupe_rows

        # Create test CSV
        csv_file = tmp_path / "leads.csv"
        csv_file.write_text("name,email,city\nJohn,john@test.com,NYC\nJane,jane@test.com,LA\n")

        rows = load_csv(str(csv_file))
        assert len(rows) == 3  # header + 2 data rows

        deduped = dedupe_rows(rows, "email")
        assert len(deduped) == 3  # no duplicates


class TestBDRCLIExportCommand:
    """Tests for the bdr export csv-to-sheets CLI command."""

    def test_export_subcommand_exists(self):
        """bdr CLI should have export subcommand."""
        from src.bdr.cli import app, export_app

        assert export_app is not None
        # Check export is registered
        assert any(cmd.name == "export" for cmd in app.registered_groups)

    def test_csv_to_sheets_command_exists(self):
        """export subcommand should have csv-to-sheets."""
        from src.bdr.cli import export_app

        # Check csv-to-sheets is a command
        cmd_names = [cmd.name for cmd in export_app.registered_commands]
        assert "csv-to-sheets" in cmd_names

    def test_csv_to_sheets_help_shows_golden_path(self, capsys):
        """csv-to-sheets --help should mention golden path."""
        from typer.testing import CliRunner

        from src.bdr.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["export", "csv-to-sheets", "--help"])

        assert result.exit_code == 0
        assert "GOLDEN PATH" in result.stdout
        assert "GOOGLE_SHEETS_CREDENTIALS_PATH" in result.stdout

    def test_csv_to_sheets_dry_run_works(self, tmp_path):
        """csv-to-sheets --dry-run should work without credentials."""
        from typer.testing import CliRunner

        from src.bdr.cli import app

        # Create test CSV
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,email\nJohn,john@test.com\n")

        runner = CliRunner()
        result = runner.invoke(app, ["export", "csv-to-sheets", str(csv_file), "--dry-run"])

        assert result.exit_code == 0
        assert "Dry run" in result.stdout

    def test_csv_to_sheets_missing_file_error(self):
        """csv-to-sheets with missing file should show clear error."""
        from typer.testing import CliRunner

        from src.bdr.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["export", "csv-to-sheets", "/nonexistent/file.csv"])

        assert result.exit_code != 0


class TestMockedGSheetsExport:
    """Tests with mocked Google Sheets client (no network calls)."""

    def test_export_csv_calls_append_rows(self, tmp_path, monkeypatch):
        """export_csv_to_sheets should call append_rows with correct data."""
        from tools.gsheets_exporter import is_gsheets_available

        if not is_gsheets_available():
            pytest.skip("GSheets deps not installed")

        # Create test CSV
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,email\nJohn,john@test.com\nJane,jane@test.com\n")

        # Create mock credentials
        creds_file = tmp_path / "creds.json"
        creds_file.write_text('{"type": "service_account"}')
        monkeypatch.setenv("GOOGLE_SHEETS_CREDENTIALS_PATH", str(creds_file))

        # Create mock gspread client
        mock_worksheet = MagicMock()
        mock_worksheet.get_all_values.return_value = []  # Empty sheet
        mock_spreadsheet = MagicMock()
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        mock_spreadsheet.worksheets.return_value = [MagicMock(title="leads")]
        mock_client = MagicMock()
        mock_client.open_by_key.return_value = mock_spreadsheet

        # Patch _get_repo_root to avoid creds-in-repo check
        fake_repo = tmp_path / "repo"
        fake_repo.mkdir()
        (fake_repo / ".git").mkdir()

        with patch("tools.gsheets_exporter._check_venv_guardrail"):
            with patch("tools.gsheets_exporter._get_repo_root", return_value=fake_repo):
                with patch("tools.gsheets_exporter.gspread.authorize", return_value=mock_client):
                    with patch("tools.gsheets_exporter.Credentials.from_service_account_file"):
                        from tools.gsheets_exporter import export_csv_to_sheets

                        row_count, mapping_info = export_csv_to_sheets(
                            csv_path=str(csv_file),
                            spreadsheet_id="test-sheet-id",
                            worksheet="leads",
                        )

        # Verify append_rows was called
        mock_worksheet.append_rows.assert_called_once()

        # Check the data passed
        call_args = mock_worksheet.append_rows.call_args[0][0]
        assert call_args[0][0] == "name"  # header
        assert len(call_args) == 3  # header + 2 rows

    def test_export_csv_replace_mode_clears_sheet(self, tmp_path, monkeypatch):
        """export_csv_to_sheets with mode=replace should clear sheet first."""
        from tools.gsheets_exporter import is_gsheets_available

        if not is_gsheets_available():
            pytest.skip("GSheets deps not installed")

        # Create test CSV
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,email\nJohn,john@test.com\n")

        # Create mock credentials
        creds_file = tmp_path / "creds.json"
        creds_file.write_text('{"type": "service_account"}')
        monkeypatch.setenv("GOOGLE_SHEETS_CREDENTIALS_PATH", str(creds_file))

        # Create mock
        mock_worksheet = MagicMock()
        mock_spreadsheet = MagicMock()
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        mock_spreadsheet.worksheets.return_value = [MagicMock(title="leads")]
        mock_client = MagicMock()
        mock_client.open_by_key.return_value = mock_spreadsheet

        fake_repo = tmp_path / "repo"
        fake_repo.mkdir()
        (fake_repo / ".git").mkdir()

        with patch("tools.gsheets_exporter._check_venv_guardrail"):
            with patch("tools.gsheets_exporter._get_repo_root", return_value=fake_repo):
                with patch("tools.gsheets_exporter.gspread.authorize", return_value=mock_client):
                    with patch("tools.gsheets_exporter.Credentials.from_service_account_file"):
                        from tools.gsheets_exporter import export_csv_to_sheets

                        export_csv_to_sheets(
                            csv_path=str(csv_file),
                            spreadsheet_id="test-sheet-id",
                            worksheet="leads",
                            mode="replace",
                        )

        # Verify clear was called before update
        mock_worksheet.clear.assert_called_once()
        mock_worksheet.update.assert_called_once()
