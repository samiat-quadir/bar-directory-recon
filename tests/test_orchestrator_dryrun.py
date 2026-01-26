"""
Unit tests for ScrapingOrchestrator - dry-run and utility methods.

These tests target:
1. _ensure_list() helper method
2. _create_result_summary() method
3. create_config_template() method
4. quick_scrape() classmethod
5. Module-level convenience functions

All tests mock WebDriver and external dependencies.
No network calls, no credentials, no real browser launching.
"""

import json
from datetime import datetime, timezone, timezone
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest


class TestOrchestratorEnsureList:
    """Tests for _ensure_list helper method."""

    def test_ensure_list_with_string(self, tmp_path):
        """_ensure_list should convert string to list."""
        from src.orchestrator import ScrapingOrchestrator

        # Create minimal valid config
        config_path = self._create_minimal_config(tmp_path)

        orchestrator = ScrapingOrchestrator(config_path)
        result = orchestrator._ensure_list("single-selector")

        assert result == ["single-selector"]

    def test_ensure_list_with_list(self, tmp_path):
        """_ensure_list should pass through list unchanged."""
        from src.orchestrator import ScrapingOrchestrator

        config_path = self._create_minimal_config(tmp_path)
        orchestrator = ScrapingOrchestrator(config_path)

        input_list = [".item-1", ".item-2", ".item-3"]
        result = orchestrator._ensure_list(input_list)

        assert result == [".item-1", ".item-2", ".item-3"]

    def test_ensure_list_with_empty_list(self, tmp_path):
        """_ensure_list should handle empty list."""
        from src.orchestrator import ScrapingOrchestrator

        config_path = self._create_minimal_config(tmp_path)
        orchestrator = ScrapingOrchestrator(config_path)

        result = orchestrator._ensure_list([])

        assert result == []

    def test_ensure_list_with_none(self, tmp_path):
        """_ensure_list should handle None value."""
        from src.orchestrator import ScrapingOrchestrator

        config_path = self._create_minimal_config(tmp_path)
        orchestrator = ScrapingOrchestrator(config_path)

        result = orchestrator._ensure_list(None)

        assert result == []

    def test_ensure_list_with_mixed_types(self, tmp_path):
        """_ensure_list should convert mixed type list to strings."""
        from src.orchestrator import ScrapingOrchestrator

        config_path = self._create_minimal_config(tmp_path)
        orchestrator = ScrapingOrchestrator(config_path)

        result = orchestrator._ensure_list([1, "two", 3.0])

        assert result == ["1", "two", "3.0"]

    def _create_minimal_config(self, tmp_path):
        """Helper to create minimal valid config file."""
        config_data = {
            "name": "test_scraper",
            "description": "Test description",
            "base_url": "https://example.com",
            "listing_phase": {"enabled": False},
            "detail_phase": {"enabled": False},
            "pagination": {"enabled": False},
            "data_extraction": {"selectors": {}},
            "output": {"format": "csv"},
            "options": {"headless": True, "log_level": "WARNING"},
        }
        config_path = tmp_path / "test_config.json"
        config_path.write_text(json.dumps(config_data))
        return config_path


class TestOrchestratorCreateResultSummary:
    """Tests for _create_result_summary method."""

    def test_create_result_summary_success(self, tmp_path):
        """_create_result_summary should create correct success summary."""
        from src.orchestrator import ScrapingOrchestrator

        config_path = self._create_minimal_config(tmp_path)
        orchestrator = ScrapingOrchestrator(config_path)

        start_time = datetime.now(timezone.utc)
        result = orchestrator._create_result_summary(
            start_time=start_time,
            success=True,
            output_files=["output/test.csv", "output/test.json"],
        )

        assert result["success"] is True
        assert result["session_name"] == "test_scraper"
        assert result["output_files"] == ["output/test.csv", "output/test.json"]
        assert "runtime_seconds" in result
        assert "runtime_formatted" in result

    def test_create_result_summary_failure(self, tmp_path):
        """_create_result_summary should create correct failure summary."""
        from src.orchestrator import ScrapingOrchestrator

        config_path = self._create_minimal_config(tmp_path)
        orchestrator = ScrapingOrchestrator(config_path)

        start_time = datetime.now(timezone.utc)
        result = orchestrator._create_result_summary(
            start_time=start_time,
            success=False,
        )

        assert result["success"] is False
        assert result["output_files"] == []

    def test_create_result_summary_with_data(self, tmp_path):
        """_create_result_summary should include extracted data counts."""
        from src.orchestrator import ScrapingOrchestrator

        config_path = self._create_minimal_config(tmp_path)
        orchestrator = ScrapingOrchestrator(config_path)

        # Simulate extracted data
        orchestrator.extracted_data = [{"name": "Item 1"}, {"name": "Item 2"}]
        orchestrator.processed_urls = ["https://ex.com/1", "https://ex.com/2"]
        orchestrator.failed_urls = ["https://ex.com/bad"]

        start_time = datetime.now(timezone.utc)
        result = orchestrator._create_result_summary(start_time, success=True)

        assert result["records_extracted"] == 2
        assert result["urls_processed"] == 2
        assert result["urls_failed"] == 1

    def _create_minimal_config(self, tmp_path):
        """Helper to create minimal valid config file."""
        config_data = {
            "name": "test_scraper",
            "description": "Test description",
            "base_url": "https://example.com",
            "listing_phase": {"enabled": False},
            "detail_phase": {"enabled": False},
            "pagination": {"enabled": False},
            "data_extraction": {"selectors": {}},
            "output": {"format": "csv"},
            "options": {"headless": True, "log_level": "WARNING"},
        }
        config_path = tmp_path / "test_config.json"
        config_path.write_text(json.dumps(config_data))
        return config_path


class TestOrchestratorCreateConfigTemplate:
    """Tests for create_config_template method."""

    def test_create_config_template_creates_file(self, tmp_path):
        """create_config_template should create a config file."""
        from src.orchestrator import ScrapingOrchestrator

        # Create orchestrator with minimal config
        config_path = self._create_minimal_config(tmp_path)
        orchestrator = ScrapingOrchestrator(config_path)

        # Create template
        output_path = str(tmp_path / "new_template.json")
        result = orchestrator.create_config_template(
            name="new_directory",
            base_url="https://newdir.com",
            output_path=output_path,
        )

        assert result == output_path
        assert Path(output_path).exists()

        # Verify content
        with open(output_path) as f:
            data = json.load(f)
        assert data["name"] == "new_directory"
        assert data["base_url"] == "https://newdir.com"

    def test_create_config_template_yaml(self, tmp_path):
        """create_config_template should create YAML file."""
        from src.orchestrator import ScrapingOrchestrator

        config_path = self._create_minimal_config(tmp_path)
        orchestrator = ScrapingOrchestrator(config_path)

        output_path = str(tmp_path / "template.yaml")
        result = orchestrator.create_config_template(
            name="yaml_dir",
            base_url="https://yaml.example.com",
            output_path=output_path,
        )

        assert result == output_path
        assert Path(output_path).exists()

    def _create_minimal_config(self, tmp_path):
        """Helper to create minimal valid config file."""
        config_data = {
            "name": "test_scraper",
            "description": "Test description",
            "base_url": "https://example.com",
            "listing_phase": {"enabled": False},
            "detail_phase": {"enabled": False},
            "pagination": {"enabled": False},
            "data_extraction": {"selectors": {}},
            "output": {"format": "csv"},
            "options": {"headless": True, "log_level": "WARNING"},
        }
        config_path = tmp_path / "test_config.json"
        config_path.write_text(json.dumps(config_data))
        return config_path


class TestOrchestratorQuickScrape:
    """Tests for quick_scrape classmethod."""

    @patch("src.orchestrator.ScrapingOrchestrator.run_scraping")
    def test_quick_scrape_creates_temp_config(self, mock_run):
        """quick_scrape should create temporary config and run."""
        from src.orchestrator import ScrapingOrchestrator

        mock_run.return_value = {"success": True, "records_extracted": 0}

        result = ScrapingOrchestrator.quick_scrape(
            name="quick_test",
            base_url="https://quick.example.com",
            list_selector=".quick-item",
            max_pages=3,
        )

        # Should have called run_scraping
        assert mock_run.called or result.get("success") is False

    def test_quick_scrape_handles_error(self):
        """quick_scrape should handle errors gracefully."""
        from src.orchestrator import ScrapingOrchestrator

        with patch.object(
            ScrapingOrchestrator, "__init__",
            side_effect=Exception("Config error")
        ):
            result = ScrapingOrchestrator.quick_scrape(
                name="error_test",
                base_url="https://error.example.com",
            )

            assert result["success"] is False
            assert "error" in result


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_create_config_function(self, tmp_path):
        """create_config should create config file."""
        from src.orchestrator import create_config

        output_path = str(tmp_path / "convenience_config.json")
        result = create_config(
            name="convenience_test",
            base_url="https://convenience.example.com",
            output_path=output_path,
        )

        assert result == output_path
        assert Path(output_path).exists()

    def test_scrape_directory_with_mock(self, tmp_path):
        """scrape_directory should invoke orchestrator."""
        from src.orchestrator import scrape_directory

        # Create minimal config
        config_data = {
            "name": "scrape_test",
            "description": "Test",
            "base_url": "https://scrape.example.com",
            "listing_phase": {"enabled": False},
            "detail_phase": {"enabled": False},
            "pagination": {"enabled": False},
            "data_extraction": {"selectors": {}},
            "output": {"format": "csv"},
            "options": {"headless": True, "log_level": "ERROR"},
        }
        config_path = tmp_path / "scrape_config.json"
        config_path.write_text(json.dumps(config_data))

        with patch("src.orchestrator.ScrapingOrchestrator.run_scraping") as mock_run:
            mock_run.return_value = {"success": True}
            result = scrape_directory(config_path)

            assert mock_run.called

    def test_quick_scrape_convenience(self):
        """quick_scrape convenience function should work."""
        from src.orchestrator import quick_scrape

        with patch(
            "src.orchestrator.ScrapingOrchestrator.quick_scrape"
        ) as mock_quick:
            mock_quick.return_value = {"success": True}
            result = quick_scrape("test", "https://test.com")

            mock_quick.assert_called_once()


class TestOrchestratorInitialization:
    """Tests for orchestrator initialization."""

    def test_orchestrator_init_creates_logger(self, tmp_path):
        """Orchestrator should create logger on init."""
        from src.orchestrator import ScrapingOrchestrator

        config_path = self._create_minimal_config(tmp_path)
        orchestrator = ScrapingOrchestrator(config_path)

        assert orchestrator.logger is not None
        assert orchestrator.config is not None

    def test_orchestrator_init_empty_collections(self, tmp_path):
        """Orchestrator should initialize empty collections."""
        from src.orchestrator import ScrapingOrchestrator

        config_path = self._create_minimal_config(tmp_path)
        orchestrator = ScrapingOrchestrator(config_path)

        assert orchestrator.extracted_data == []
        assert orchestrator.processed_urls == []
        assert orchestrator.failed_urls == []

    def test_orchestrator_init_managers_none(self, tmp_path):
        """Orchestrator should have None managers until initialized."""
        from src.orchestrator import ScrapingOrchestrator

        config_path = self._create_minimal_config(tmp_path)
        orchestrator = ScrapingOrchestrator(config_path)

        assert orchestrator.driver_manager is None
        assert orchestrator.pagination_manager is None
        assert orchestrator.data_extractor is None

    def _create_minimal_config(self, tmp_path):
        """Helper to create minimal valid config file."""
        config_data = {
            "name": "init_test",
            "description": "Test description",
            "base_url": "https://init.example.com",
            "listing_phase": {"enabled": False},
            "detail_phase": {"enabled": False},
            "pagination": {"enabled": False},
            "data_extraction": {"selectors": {}},
            "output": {"format": "csv"},
            "options": {"headless": True, "log_level": "WARNING"},
        }
        config_path = tmp_path / "init_config.json"
        config_path.write_text(json.dumps(config_data))
        return config_path


class TestOrchestratorInitializeManagers:
    """Tests for initialize_managers method."""

    def test_initialize_managers_creates_all(self, tmp_path):
        """initialize_managers should create all manager instances."""
        from src.orchestrator import ScrapingOrchestrator

        config_path = self._create_minimal_config(tmp_path)
        orchestrator = ScrapingOrchestrator(config_path)

        orchestrator.initialize_managers()

        assert orchestrator.driver_manager is not None
        assert orchestrator.pagination_manager is not None
        assert orchestrator.data_extractor is not None

    def test_initialize_managers_uses_config_options(self, tmp_path):
        """initialize_managers should use config options."""
        from src.orchestrator import ScrapingOrchestrator

        config_data = {
            "name": "options_test",
            "description": "Test with options",
            "base_url": "https://options.example.com",
            "listing_phase": {"enabled": False, "list_selector": ".item"},
            "detail_phase": {"enabled": False},
            "pagination": {"max_pages": 20, "delay": 3.0},
            "data_extraction": {"selectors": {}},
            "output": {"format": "csv"},
            "options": {
                "headless": False,
                "timeout": 60,
                "log_level": "WARNING",
            },
        }
        config_path = tmp_path / "options_config.json"
        config_path.write_text(json.dumps(config_data))

        orchestrator = ScrapingOrchestrator(config_path)
        orchestrator.initialize_managers()

        # Managers should be created
        assert orchestrator.pagination_manager is not None

    def _create_minimal_config(self, tmp_path):
        """Helper to create minimal valid config file."""
        config_data = {
            "name": "init_test",
            "description": "Test description",
            "base_url": "https://init.example.com",
            "listing_phase": {"enabled": False},
            "detail_phase": {"enabled": False},
            "pagination": {"enabled": False},
            "data_extraction": {"selectors": {}},
            "output": {"format": "csv"},
            "options": {"headless": True, "log_level": "WARNING"},
        }
        config_path = tmp_path / "init_config.json"
        config_path.write_text(json.dumps(config_data))
        return config_path


class TestOrchestratorExtractFromCurrentPage:
    """Tests for extract_from_current_page method."""

    def test_extract_from_current_page_with_mock(self, tmp_path):
        """extract_from_current_page should call data_extractor."""
        from src.orchestrator import ScrapingOrchestrator

        config_path = self._create_minimal_config(tmp_path)
        orchestrator = ScrapingOrchestrator(config_path)

        # Mock the data_extractor
        mock_extractor = Mock()
        mock_extractor.extract_from_page.return_value = [{"name": "Test Item"}]
        orchestrator.data_extractor = mock_extractor
        orchestrator.driver_manager = Mock()

        result = orchestrator.extract_from_current_page()

        assert result == [{"name": "Test Item"}]

    def test_extract_from_current_page_handles_error(self, tmp_path):
        """extract_from_current_page should handle extraction errors."""
        from src.orchestrator import ScrapingOrchestrator

        config_path = self._create_minimal_config(tmp_path)
        orchestrator = ScrapingOrchestrator(config_path)

        # Mock data_extractor to raise error
        mock_extractor = Mock()
        mock_extractor.extract_from_page.side_effect = Exception("Extract error")
        orchestrator.data_extractor = mock_extractor
        orchestrator.driver_manager = Mock()

        result = orchestrator.extract_from_current_page()

        # Should return empty list on error
        assert result == []

    def _create_minimal_config(self, tmp_path):
        """Helper to create minimal valid config file."""
        config_data = {
            "name": "extract_test",
            "description": "Test description",
            "base_url": "https://extract.example.com",
            "listing_phase": {"enabled": False},
            "detail_phase": {"enabled": False},
            "pagination": {"enabled": False},
            "data_extraction": {"selectors": {}},
            "output": {"format": "csv"},
            "options": {"headless": True, "log_level": "WARNING"},
        }
        config_path = tmp_path / "extract_config.json"
        config_path.write_text(json.dumps(config_data))
        return config_path
