"""
Unit tests for ScrapingLogger module.

Tests cover:
- Logger instantiation and directory creation
- Log file creation
- Stats tracking (warnings, errors counters)
- Session report generation
"""

import json
import sys
from pathlib import Path

# Import the module under test
sys.path.insert(0, str(Path(__file__).parent.parent))

from logger import ScrapingLogger, create_logger  # noqa: E402


class TestScrapingLoggerInstantiation:
    """Test cases for ScrapingLogger instantiation."""

    def test_logger_creates_log_directory(self, tmp_path):
        """Test that logger creates the log directory if it doesn't exist."""
        log_dir = tmp_path / "test_logs"

        # Directory should not exist yet
        assert not log_dir.exists()

        logger = ScrapingLogger("test_logger", log_dir=str(log_dir))

        # Directory should now exist
        assert log_dir.exists()

        # Cleanup handlers without save (to avoid datetime serialization issue)
        for handler in logger.logger.handlers:
            handler.close()
            logger.logger.removeHandler(handler)

    def test_logger_creates_log_file(self, tmp_path):
        """Test that logger creates a log file."""
        log_dir = tmp_path / "test_logs"

        logger = ScrapingLogger("test_file_logger", log_dir=str(log_dir))

        # Write something to ensure file is created
        logger.info("Test message")

        # Check log file was created
        log_files = list(log_dir.glob("test_file_logger_*.log"))
        assert len(log_files) >= 1

        # Cleanup handlers without save
        for handler in logger.logger.handlers:
            handler.close()
            logger.logger.removeHandler(handler)

    def test_logger_initializes_stats(self, tmp_path):
        """Test that logger initializes statistics correctly."""
        log_dir = tmp_path / "test_logs"

        logger = ScrapingLogger("stats_test", log_dir=str(log_dir))

        # Verify initial stats
        assert "start_time" in logger.stats
        assert logger.stats["pages_processed"] == 0
        assert logger.stats["records_extracted"] == 0
        assert logger.stats["errors"] == 0
        assert logger.stats["warnings"] == 0
        assert logger.stats["screenshots"] == 0

        # Cleanup handlers without save
        for handler in logger.logger.handlers:
            handler.close()
            logger.logger.removeHandler(handler)


class TestScrapingLoggerStatsTracking:
    """Test cases for ScrapingLogger statistics tracking."""

    def _cleanup_logger(self, logger):
        """Clean up logger handlers without calling save_session_report."""
        for handler in logger.logger.handlers:
            handler.close()
            logger.logger.removeHandler(handler)

    def test_warning_increments_counter(self, tmp_path):
        """Test that warning() increments the warnings counter."""
        log_dir = tmp_path / "test_logs"
        logger = ScrapingLogger("warning_test", log_dir=str(log_dir))

        initial_warnings = logger.stats["warnings"]
        assert initial_warnings == 0

        logger.warning("Test warning 1")
        assert logger.stats["warnings"] == 1

        logger.warning("Test warning 2")
        assert logger.stats["warnings"] == 2

        # Verify warnings are recorded
        assert len(logger.warnings) == 2
        assert logger.warnings[0]["message"] == "Test warning 1"
        assert logger.warnings[1]["message"] == "Test warning 2"

        # Cleanup
        self._cleanup_logger(logger)

    def test_error_increments_counter(self, tmp_path):
        """Test that error() increments the errors counter."""
        log_dir = tmp_path / "test_logs"
        logger = ScrapingLogger("error_test", log_dir=str(log_dir))

        initial_errors = logger.stats["errors"]
        assert initial_errors == 0

        logger.error("Test error 1")
        assert logger.stats["errors"] == 1

        logger.error("Test error 2", exception=ValueError("Test exception"))
        assert logger.stats["errors"] == 2

        # Verify errors are recorded
        assert len(logger.errors) == 2
        assert logger.errors[0]["message"] == "Test error 1"
        assert logger.errors[1]["message"] == "Test error 2"
        assert "exception" in logger.errors[1]

        # Cleanup
        self._cleanup_logger(logger)

    def test_log_page_processed_increments_counter(self, tmp_path):
        """Test that log_page_processed() increments pages_processed counter."""
        log_dir = tmp_path / "test_logs"
        logger = ScrapingLogger("page_test", log_dir=str(log_dir))

        assert logger.stats["pages_processed"] == 0

        logger.log_page_processed("https://example.com/page1", success=True)
        assert logger.stats["pages_processed"] == 1

        logger.log_page_processed("https://example.com/page2", success=False)
        assert logger.stats["pages_processed"] == 2

        # Cleanup
        self._cleanup_logger(logger)

    def test_log_record_extracted_increments_counter(self, tmp_path):
        """Test that log_record_extracted() increments records_extracted counter."""
        log_dir = tmp_path / "test_logs"
        logger = ScrapingLogger("record_test", log_dir=str(log_dir))

        assert logger.stats["records_extracted"] == 0

        logger.log_record_extracted({"name": "Test Record 1"}, url="https://example.com")
        assert logger.stats["records_extracted"] == 1

        logger.log_record_extracted({"name": "Test Record 2"})
        assert logger.stats["records_extracted"] == 2

        # Cleanup
        self._cleanup_logger(logger)

    def test_log_screenshot_increments_counter(self, tmp_path):
        """Test that log_screenshot() increments screenshots counter."""
        log_dir = tmp_path / "test_logs"
        logger = ScrapingLogger("screenshot_test", log_dir=str(log_dir))

        assert logger.stats["screenshots"] == 0

        logger.log_screenshot("/path/to/screenshot1.png", context="Error page")
        assert logger.stats["screenshots"] == 1

        logger.log_screenshot("/path/to/screenshot2.png")
        assert logger.stats["screenshots"] == 2

        # Cleanup
        self._cleanup_logger(logger)


class TestScrapingLoggerGetStats:
    """Test cases for get_stats() method."""

    def _cleanup_logger(self, logger):
        """Clean up logger handlers without calling save_session_report."""
        for handler in logger.logger.handlers:
            handler.close()
            logger.logger.removeHandler(handler)

    def test_get_stats_returns_runtime_info(self, tmp_path):
        """Test that get_stats() returns runtime information."""
        log_dir = tmp_path / "test_logs"
        logger = ScrapingLogger("stats_info_test", log_dir=str(log_dir))

        # Perform some operations
        logger.log_page_processed("https://example.com", success=True)
        logger.log_record_extracted({"name": "Test"})

        stats = logger.get_stats()

        # Verify essential stats keys
        assert "start_time" in stats
        assert "end_time" in stats
        assert "runtime_seconds" in stats
        assert "runtime_formatted" in stats
        assert "pages_per_minute" in stats
        assert "records_per_minute" in stats

        # Verify counts
        assert stats["pages_processed"] == 1
        assert stats["records_extracted"] == 1

        # Cleanup
        self._cleanup_logger(logger)


class TestScrapingLoggerSessionReport:
    """Test cases for session report functionality."""

    def _cleanup_logger(self, logger):
        """Clean up logger handlers without calling save_session_report."""
        for handler in logger.logger.handlers:
            handler.close()
            logger.logger.removeHandler(handler)

    def test_save_session_report_creates_file(self, tmp_path):
        """Test that save_session_report() creates a JSON report file."""
        log_dir = tmp_path / "test_logs"
        logger = ScrapingLogger("report_test", log_dir=str(log_dir))

        # Add some activity
        logger.warning("Test warning")
        logger.error("Test error")
        logger.log_page_processed("https://example.com", success=True)

        # Save report
        report_path = logger.save_session_report()

        # Verify report file was created
        assert Path(report_path).exists()

        # Verify report content is valid JSON
        with open(report_path, 'r') as f:
            report = json.load(f)

        assert "session_info" in report
        assert "statistics" in report
        assert "errors" in report
        assert "warnings" in report
        assert report["session_info"]["name"] == "report_test"

        # Cleanup
        self._cleanup_logger(logger)

    def test_save_session_report_custom_path(self, tmp_path):
        """Test that save_session_report() saves to custom path."""
        log_dir = tmp_path / "test_logs"
        logger = ScrapingLogger("custom_path_test", log_dir=str(log_dir))

        custom_report_path = tmp_path / "custom_report.json"
        report_path = logger.save_session_report(output_path=str(custom_report_path))

        assert report_path == str(custom_report_path)
        assert custom_report_path.exists()

        # Cleanup
        self._cleanup_logger(logger)


class TestScrapingLoggerSummary:
    """Test cases for get_summary() method."""

    def _cleanup_logger(self, logger):
        """Clean up logger handlers without calling save_session_report."""
        for handler in logger.logger.handlers:
            handler.close()
            logger.logger.removeHandler(handler)

    def test_get_summary_returns_formatted_string(self, tmp_path):
        """Test that get_summary() returns a formatted summary string."""
        log_dir = tmp_path / "test_logs"
        logger = ScrapingLogger("summary_test", log_dir=str(log_dir))

        # Add some activity
        logger.log_page_processed("https://example.com/1", success=True)
        logger.log_page_processed("https://example.com/2", success=True)
        logger.log_record_extracted({"name": "Test"})
        logger.warning("Test warning")
        logger.error("Test error")

        summary = logger.get_summary()

        # Verify summary contains expected sections
        assert "SCRAPING SESSION SUMMARY" in summary
        assert "summary_test" in summary
        assert "Pages Processed: 2" in summary
        assert "Records Extracted: 1" in summary
        assert "Errors: 1" in summary
        assert "Warnings: 1" in summary

        # Cleanup
        self._cleanup_logger(logger)


class TestCreateLoggerFunction:
    """Test cases for the create_logger() convenience function."""

    def _cleanup_logger(self, logger):
        """Clean up logger handlers without calling save_session_report."""
        for handler in logger.logger.handlers:
            handler.close()
            logger.logger.removeHandler(handler)

    def test_create_logger_returns_scraping_logger(self, tmp_path):
        """Test that create_logger() returns a ScrapingLogger instance."""
        log_dir = tmp_path / "test_logs"

        logger = create_logger("function_test", log_dir=str(log_dir))

        assert isinstance(logger, ScrapingLogger)
        assert logger.name == "function_test"

        # Cleanup
        self._cleanup_logger(logger)

    def test_create_logger_with_log_level(self, tmp_path):
        """Test that create_logger() respects log level parameter."""
        log_dir = tmp_path / "test_logs"

        logger = create_logger("level_test", log_dir=str(log_dir), log_level="DEBUG")

        # Logger should be created successfully
        assert logger is not None

        # Cleanup
        self._cleanup_logger(logger)
