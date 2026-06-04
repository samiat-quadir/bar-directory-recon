"""
Tests for gsheets_exporter guardrails and env var deprecation behavior.

These tests verify:
1. Venv guardrail raises RuntimeError when outside project venv
2. Legacy GOOGLE_SA_JSON env var triggers DeprecationWarning
3. Credential validation rejects credentials inside repo
4. GSheetsNotInstalledError is raised when dependencies missing
"""

import sys
from unittest.mock import patch

import pytest


class TestGSheetsAvailability:
    """Tests for dependency availability checking."""

    def test_is_gsheets_available_returns_bool(self):
        """is_gsheets_available should return a boolean."""
        from tools.gsheets_exporter import is_gsheets_available

        result = is_gsheets_available()
        assert isinstance(result, bool)

    def test_check_gsheets_available_caches_result(self):
        """_check_gsheets_available should cache its result."""
        import tools.gsheets_exporter as exporter

        # Reset cache
        exporter._GSHEETS_AVAILABLE = None

        # First call
        result1 = exporter._check_gsheets_available()
        # Second call should use cache
        result2 = exporter._check_gsheets_available()

        assert result1 == result2
        # Cache should be set
        assert exporter._GSHEETS_AVAILABLE is not None


class TestVenvGuardrailBehavior:
    """Tests for interpreter/venv guardrail behavior."""

    def test_guardrail_raises_when_outside_project_venv(self, tmp_path, monkeypatch):
        """Guardrail should raise RuntimeError when not in project venv."""
        from tools.gsheets_exporter import _check_venv_guardrail

        # Create fake repo structure
        repo_root = tmp_path / "project"
        repo_root.mkdir()
        (repo_root / ".git").mkdir()

        # Set VIRTUAL_ENV to something NOT in the project
        other_venv = tmp_path / "other_venv"
        other_venv.mkdir()
        monkeypatch.setenv("VIRTUAL_ENV", str(other_venv))

        # Mock sys.executable to be outside project too
        with patch.object(sys, "executable", str(other_venv / "python.exe")):
            with patch("tools.gsheets_exporter._get_repo_root", return_value=repo_root):
                with pytest.raises(RuntimeError) as exc_info:
                    _check_venv_guardrail()

        error_msg = str(exc_info.value)
        assert "INTERPRETER ERROR" in error_msg
        assert "virtual environment" in error_msg.lower()

    def test_guardrail_passes_with_venv_alt_path(self, tmp_path, monkeypatch):
        """Guardrail should pass when using 'venv' instead of '.venv'."""
        from tools.gsheets_exporter import _check_venv_guardrail

        repo_root = tmp_path / "project"
        repo_root.mkdir()
        (repo_root / ".git").mkdir()

        # Use 'venv' not '.venv'
        venv_path = repo_root / "venv"
        venv_path.mkdir()

        monkeypatch.setenv("VIRTUAL_ENV", str(venv_path))

        with patch("tools.gsheets_exporter._get_repo_root", return_value=repo_root):
            # Should not raise
            _check_venv_guardrail()


class TestCredentialValidation:
    """Tests for credential path validation."""

    def test_validate_credentials_rejects_creds_in_repo(self, tmp_path):
        """Credentials inside the repository should be rejected."""
        from tools.gsheets_exporter import _validate_credentials_path

        repo_root = tmp_path / "project"
        repo_root.mkdir()
        (repo_root / ".git").mkdir()

        # Create creds inside repo
        creds_inside = repo_root / "secrets" / "creds.json"
        creds_inside.parent.mkdir(parents=True)
        creds_inside.write_text("{}")

        with pytest.raises(ValueError) as exc_info:
            _validate_credentials_path(str(creds_inside), str(repo_root))

        error_msg = str(exc_info.value)
        assert "SECURITY ERROR" in error_msg
        assert "inside the repository" in error_msg.lower()

    def test_validate_credentials_accepts_creds_outside_repo(self, tmp_path):
        """Credentials outside the repository should be accepted."""
        from tools.gsheets_exporter import _validate_credentials_path

        repo_root = tmp_path / "project"
        repo_root.mkdir()
        (repo_root / ".git").mkdir()

        # Create creds outside repo
        secrets_dir = tmp_path / "secrets"
        secrets_dir.mkdir()
        creds_outside = secrets_dir / "creds.json"
        creds_outside.write_text("{}")

        # Should not raise
        _validate_credentials_path(str(creds_outside), str(repo_root))


class TestLegacyEnvVarDeprecation:
    """Tests for legacy environment variable deprecation."""

    def test_legacy_google_sa_json_triggers_warning(self, tmp_path, monkeypatch):
        """Using GOOGLE_SA_JSON should emit DeprecationWarning."""
        from tools.gsheets_exporter import get_client, is_gsheets_available

        if not is_gsheets_available():
            pytest.skip("GSheets dependencies not installed")

        # Create credentials outside "repo"
        secrets_dir = tmp_path / "secrets"
        secrets_dir.mkdir()
        creds_file = secrets_dir / "sa.json"
        creds_file.write_text('{"type": "service_account"}')

        # Clear new var, set legacy var
        monkeypatch.delenv("GOOGLE_SHEETS_CREDENTIALS_PATH", raising=False)
        monkeypatch.setenv("GOOGLE_SA_JSON", str(creds_file))

        # Set up fake repo
        fake_repo = tmp_path / "repo"
        fake_repo.mkdir()
        (fake_repo / ".git").mkdir()

        with patch("tools.gsheets_exporter._check_venv_guardrail"):
            with patch("tools.gsheets_exporter._get_repo_root", return_value=fake_repo):
                with pytest.warns(DeprecationWarning, match="GOOGLE_SA_JSON.*deprecated"):
                    try:
                        get_client()
                    except Exception:
                        pass  # Auth will fail, we only want the warning


class TestGSheetsExceptions:
    """Tests for custom exception classes."""

    def test_gsheets_not_installed_error_message(self):
        """GSheetsNotInstalledError should have helpful message."""
        from tools.gsheets_exporter import GSheetsNotInstalledError

        error = GSheetsNotInstalledError()
        msg = str(error)

        assert "not installed" in msg.lower()
        assert "pip install" in msg

    def test_worksheet_not_found_error_shows_available(self):
        """WorksheetNotFoundError should list available worksheets."""
        from tools.gsheets_exporter import WorksheetNotFoundError

        error = WorksheetNotFoundError(
            worksheet_name="nonexistent",
            available_worksheets=["Sheet1", "leads", "changelog"],
            spreadsheet_id="abc123"
        )
        msg = str(error)

        assert "nonexistent" in msg
        assert "Sheet1" in msg
        assert "leads" in msg
        assert "changelog" in msg

    def test_worksheet_not_found_error_suggests_first(self):
        """WorksheetNotFoundError should suggest first available worksheet."""
        from tools.gsheets_exporter import WorksheetNotFoundError

        error = WorksheetNotFoundError(
            worksheet_name="wrong",
            available_worksheets=["leads", "archive"],
        )
        msg = str(error)

        assert "--worksheet 'leads'" in msg or "leads" in msg


class TestCSVLoadingEdgeCases:
    """Tests for CSV loading edge cases."""

    def test_load_csv_file_not_found(self, tmp_path):
        """load_csv should raise FileNotFoundError for missing files."""
        from tools.gsheets_exporter import load_csv

        with pytest.raises(FileNotFoundError):
            load_csv(str(tmp_path / "nonexistent.csv"))

    def test_dedupe_rows_missing_column(self):
        """dedupe_rows should raise ValueError for missing column."""
        from tools.gsheets_exporter import dedupe_rows

        rows = [
            ["name", "email"],
            ["John", "john@test.com"],
        ]

        with pytest.raises(ValueError) as exc_info:
            dedupe_rows(rows, "phone")

        error_msg = str(exc_info.value)
        assert "phone" in error_msg
        assert "name" in error_msg  # should show available columns

    def test_dedupe_rows_single_row_returns_unchanged(self):
        """dedupe_rows with only header should return unchanged."""
        from tools.gsheets_exporter import dedupe_rows

        rows = [["name", "email"]]
        result = dedupe_rows(rows, "email")

        assert result == rows


class TestHeaderMapping:
    """Tests for CSV to Sheet header mapping."""

    def test_normalize_header_strips_whitespace(self):
        """_normalize_header should strip spaces and normalize."""
        from tools.gsheets_exporter import _normalize_header

        assert _normalize_header("  Name  ") == "name"
        assert _normalize_header("Email Address") == "email_address"
        assert _normalize_header("phone-number") == "phone_number"

    def test_header_synonyms_mapping(self):
        """HEADER_SYNONYMS should map common variations."""
        from tools.gsheets_exporter import HEADER_SYNONYMS

        assert HEADER_SYNONYMS.get("name") == "full_name"
        assert HEADER_SYNONYMS.get("fullname") == "full_name"
        assert HEADER_SYNONYMS.get("company") == "firm"
        assert HEADER_SYNONYMS.get("bar_id") == "bar_number"
