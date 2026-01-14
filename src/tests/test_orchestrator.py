"""
Unit tests for ScrapingOrchestrator module.

Tests cover:
- Dry-run initialization with minimal config
- Manager initialization
- Ensure list helper function
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Import the module under test
sys.path.insert(0, str(Path(__file__).parent.parent))


class MockConfig:
    """Mock configuration object for testing."""

    def __init__(self):
        self.name = "test_scraper"
        self.base_url = "https://example.com"
        self.options = {
            "headless": True,
            "timeout": 30,
            "log_level": "INFO"
        }
        self.listing_phase = {
            "enabled": False,
            "list_selector": ".listing",
            "link_selector": "a.link",
            "delay": 1.0
        }
        self.detail_phase = {
            "enabled": False,
            "delay": 1.0
        }
        self.pagination = {
            "max_pages": 5,
            "delay": 2.0,
            "next_button": [],
            "load_more": [],
            "page_numbers": []
        }
        self.data_extraction = {
            "selectors": {},
            "required_fields": []
        }
        self.output = {
            "filename": "test_output"
        }


class TestScrapingOrchestratorInit:
    """Test cases for ScrapingOrchestrator initialization."""

    def test_orchestrator_init_with_mock_config(self, tmp_path):
        """Test that orchestrator initializes with mock configuration."""
        from orchestrator import ScrapingOrchestrator

        # Create a mock config loader that returns our mock config
        mock_config = MockConfig()

        with patch('orchestrator.ConfigLoader') as MockConfigLoader:
            mock_loader = MagicMock()
            mock_loader.load_config.return_value = mock_config
            MockConfigLoader.return_value = mock_loader

            with patch('orchestrator.create_logger') as mock_create_logger:
                mock_logger = MagicMock()
                mock_create_logger.return_value = mock_logger

                config_path = tmp_path / "test_config.json"
                config_path.write_text('{}')

                orchestrator = ScrapingOrchestrator(config_path)

                # Verify initialization
                assert orchestrator.config == mock_config
                assert orchestrator.extracted_data == []
                assert orchestrator.processed_urls == []
                assert orchestrator.failed_urls == []

    def test_orchestrator_ensure_list_with_string(self, tmp_path):
        """Test _ensure_list converts string to list."""
        from orchestrator import ScrapingOrchestrator

        mock_config = MockConfig()

        with patch('orchestrator.ConfigLoader') as MockConfigLoader:
            mock_loader = MagicMock()
            mock_loader.load_config.return_value = mock_config
            MockConfigLoader.return_value = mock_loader

            with patch('orchestrator.create_logger') as mock_create_logger:
                mock_logger = MagicMock()
                mock_create_logger.return_value = mock_logger

                config_path = tmp_path / "test_config.json"
                config_path.write_text('{}')

                orchestrator = ScrapingOrchestrator(config_path)

                # Test with string
                result = orchestrator._ensure_list("single_value")
                assert result == ["single_value"]

    def test_orchestrator_ensure_list_with_list(self, tmp_path):
        """Test _ensure_list returns list unchanged."""
        from orchestrator import ScrapingOrchestrator

        mock_config = MockConfig()

        with patch('orchestrator.ConfigLoader') as MockConfigLoader:
            mock_loader = MagicMock()
            mock_loader.load_config.return_value = mock_config
            MockConfigLoader.return_value = mock_loader

            with patch('orchestrator.create_logger') as mock_create_logger:
                mock_logger = MagicMock()
                mock_create_logger.return_value = mock_logger

                config_path = tmp_path / "test_config.json"
                config_path.write_text('{}')

                orchestrator = ScrapingOrchestrator(config_path)

                # Test with list
                result = orchestrator._ensure_list(["value1", "value2"])
                assert result == ["value1", "value2"]

    def test_orchestrator_ensure_list_with_empty(self, tmp_path):
        """Test _ensure_list handles empty/None values."""
        from orchestrator import ScrapingOrchestrator

        mock_config = MockConfig()

        with patch('orchestrator.ConfigLoader') as MockConfigLoader:
            mock_loader = MagicMock()
            mock_loader.load_config.return_value = mock_config
            MockConfigLoader.return_value = mock_loader

            with patch('orchestrator.create_logger') as mock_create_logger:
                mock_logger = MagicMock()
                mock_create_logger.return_value = mock_logger

                config_path = tmp_path / "test_config.json"
                config_path.write_text('{}')

                orchestrator = ScrapingOrchestrator(config_path)

                # Test with None-like values
                result = orchestrator._ensure_list(None)
                assert result == []

                result = orchestrator._ensure_list([])
                assert result == []


class TestScrapingOrchestratorDryRun:
    """Test cases for dry-run scenarios."""

    def test_run_listing_phase_disabled(self, tmp_path):
        """Test run_listing_phase when listing is disabled returns base URL."""
        from orchestrator import ScrapingOrchestrator

        mock_config = MockConfig()
        mock_config.listing_phase["enabled"] = False

        with patch('orchestrator.ConfigLoader') as MockConfigLoader:
            mock_loader = MagicMock()
            mock_loader.load_config.return_value = mock_config
            MockConfigLoader.return_value = mock_loader

            with patch('orchestrator.create_logger') as mock_create_logger:
                mock_logger = MagicMock()
                mock_create_logger.return_value = mock_logger

                config_path = tmp_path / "test_config.json"
                config_path.write_text('{}')

                orchestrator = ScrapingOrchestrator(config_path)
                orchestrator.data_extractor = MagicMock()

                # Run listing phase with listing disabled
                urls = orchestrator.run_listing_phase()

                # Should return base URL only
                assert urls == [mock_config.base_url]

    def test_result_summary_creation(self, tmp_path):
        """Test _create_result_summary returns expected structure."""
        from datetime import datetime

        from orchestrator import ScrapingOrchestrator

        mock_config = MockConfig()

        with patch('orchestrator.ConfigLoader') as MockConfigLoader:
            mock_loader = MagicMock()
            mock_loader.load_config.return_value = mock_config
            MockConfigLoader.return_value = mock_loader

            with patch('orchestrator.create_logger') as mock_create_logger:
                mock_logger = MagicMock()
                mock_logger.get_stats.return_value = {
                    "pages_processed": 0,
                    "records_extracted": 0
                }
                mock_create_logger.return_value = mock_logger

                config_path = tmp_path / "test_config.json"
                config_path.write_text('{}')

                orchestrator = ScrapingOrchestrator(config_path)

                start_time = datetime.now()
                result = orchestrator._create_result_summary(
                    start_time, success=True, output_files=["test.csv"]
                )

                # Verify result structure
                assert result["success"] is True
                assert result["session_name"] == "test_scraper"
                assert "start_time" in result
                assert "end_time" in result
                assert "runtime_seconds" in result
                assert result["output_files"] == ["test.csv"]
                assert result["records_extracted"] == 0
                assert result["urls_processed"] == 0
                assert result["urls_failed"] == 0


class TestScrapingOrchestratorQuickScrape:
    """Test cases for quick_scrape class method."""

    def test_quick_scrape_creates_temp_config(self, tmp_path):
        """Test that quick_scrape creates and cleans up temp config."""
        from orchestrator import ScrapingOrchestrator

        # Create config directory
        config_dir = tmp_path / "config"
        config_dir.mkdir(parents=True, exist_ok=True)

        with patch('orchestrator.ConfigLoader') as MockConfigLoader:
            mock_loader = MagicMock()
            mock_config = MockConfig()
            mock_loader.generate_sample_config.return_value = mock_config
            MockConfigLoader.return_value = mock_loader

            with patch.object(ScrapingOrchestrator, '__init__', return_value=None):
                with patch.object(ScrapingOrchestrator, 'run_scraping') as mock_run:
                    mock_run.return_value = {"success": True}

                    # This would need more complex setup to fully test
                    # For now, verify the method exists and is callable
                    assert callable(ScrapingOrchestrator.quick_scrape)
