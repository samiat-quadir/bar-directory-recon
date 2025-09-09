#!/usr/bin/env python3
"""
Tests for the PaginationManager module.
"""

import unittest
from unittest.mock import MagicMock, patch

from selenium.webdriver.common.by import By

from src.pagination_manager import PaginationManager


class TestPaginationManager(unittest.TestCase):
    """Test cases for the PaginationManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.driver_manager = MagicMock()
        self.driver = MagicMock()
        self.driver_manager.driver = self.driver
        self.config = {
            "max_pages": 3,
            "page_delay": 0.1,
            "pagination_selectors": {
                "next_button": [".next-button", ".next-page"],
                "load_more": [".load-more", ".show-more"],
                "page_numbers": [".page-numbers a", ".pagination a"],
            },
        }
        self.pagination_manager = PaginationManager(self.driver_manager, self.config)

    def test_initialization(self):
        """Test initialization with proper config."""
        self.assertEqual(self.pagination_manager.max_pages, 3)
        self.assertEqual(self.pagination_manager.page_delay, 0.1)
        self.assertEqual(self.pagination_manager.current_page, 1)
        self.assertIn("next_button", self.pagination_manager.pagination_selectors)
        self.assertIn("load_more", self.pagination_manager.pagination_selectors)
        self.assertIn("page_numbers", self.pagination_manager.pagination_selectors)

    def test_detect_pagination_type_next_button(self):
        """Test detection of next button pagination."""
        # Mock find_elements to return a displayed button for the first selector
        self.driver.find_elements.return_value = [MagicMock(is_displayed=lambda: True)]

        result = self.pagination_manager.detect_pagination_type()
        self.assertEqual(result, "next_button")

        # Verify correct selector was checked
        self.driver.find_elements.assert_any_call(By.CSS_SELECTOR, ".next-button")

    def test_detect_pagination_type_load_more(self):
        """Test detection of load more pagination."""

        # Mock find_elements to return empty for next button but visible for load more
        def find_elements_side_effect(by, selector):
            if ".load-more" in selector:
                return [MagicMock(is_displayed=lambda: True)]
            return []

        self.driver.find_elements.side_effect = find_elements_side_effect

        result = self.pagination_manager.detect_pagination_type()
        self.assertEqual(result, "load_more")

    def test_detect_pagination_type_page_numbers(self):
        """Test detection of page numbers pagination."""

        # Mock find_elements to return empty for next button and load more, but multiple page links
        def find_elements_side_effect(by, selector):
            if any(
                page_selector in selector
                for page_selector in [".page-numbers a", ".pagination a"]
            ):
                return [MagicMock(), MagicMock()]  # Multiple page elements
            return []

        self.driver.find_elements.side_effect = find_elements_side_effect

        result = self.pagination_manager.detect_pagination_type()
        self.assertEqual(result, "page_numbers")

    def test_detect_pagination_type_infinite_scroll(self):
        """Test detection of infinite scroll pagination."""
        # Mock find_elements to return empty for all selectors
        self.driver.find_elements.return_value = []

        # Mock _has_infinite_scroll to return True
        with patch.object(
            self.pagination_manager, "_has_infinite_scroll", return_value=True
        ):
            result = self.pagination_manager.detect_pagination_type()
            self.assertEqual(result, "infinite_scroll")

    def test_detect_pagination_type_none(self):
        """Test detection of no pagination."""
        # Mock find_elements to return empty for all selectors
        self.driver.find_elements.return_value = []

        # Mock _has_infinite_scroll to return False
        with patch.object(
            self.pagination_manager, "_has_infinite_scroll", return_value=False
        ):
            result = self.pagination_manager.detect_pagination_type()
            self.assertEqual(result, "none")

    def test_has_infinite_scroll(self):
        """Test infinite scroll detection."""
        # Mock execute_script to simulate a page height change after scrolling
        self.driver.execute_script.side_effect = [
            100,  # Initial height
            200,  # New height after scrolling
        ]

        result = self.pagination_manager._has_infinite_scroll()
        self.assertTrue(result)

        # Verify correct scrolling operations
        self.driver.execute_script.assert_any_call("return document.body.scrollHeight")
        self.driver.execute_script.assert_any_call(
            "window.scrollTo(0, document.body.scrollHeight);"
        )

    def test_paginate_all_pages_none(self):
        """Test paginate_all_pages with no pagination."""
        # Mock detect_pagination_type to return "none"
        with patch.object(
            self.pagination_manager, "detect_pagination_type", return_value="none"
        ):
            pages = list(self.pagination_manager.paginate_all_pages())
            self.assertEqual(pages, [1])  # Only the first page

    def test_paginate_all_pages_next_button(self):
        """Test paginate_all_pages with next button pagination."""
        # Mock detect_pagination_type to return "next_button"
        with patch.object(
            self.pagination_manager,
            "detect_pagination_type",
            return_value="next_button",
        ):
            # Mock _paginate_next_button to yield pages 2 and 3
            with patch.object(
                self.pagination_manager,
                "_paginate_next_button",
                return_value=iter([2, 3]),
            ):
                pages = list(self.pagination_manager.paginate_all_pages())
                self.assertEqual(pages, [1, 2, 3])  # First page + next pages

    def test_paginate_next_button(self):
        """Test _paginate_next_button method."""
        # Mock click_element to succeed for first page then fail
        self.driver_manager.click_element.side_effect = [True, False]

        # Mock time.sleep to be instant
        with patch("time.sleep"):
            pages = list(self.pagination_manager._paginate_next_button())
            self.assertEqual(pages, [2])  # Only page 2 (after first page)

            # Verify click_element was called correctly
            self.driver_manager.click_element.assert_any_call(".next-button", timeout=5)

    def test_navigate_to_page_success(self):
        """Test navigate_to_page with success."""
        # Mock find_elements to return a link with matching text
        mock_link = MagicMock()
        mock_link.text = "2"
        mock_link.get_attribute.return_value = None
        self.driver.find_elements.return_value = [mock_link]

        # Mock time.sleep to be instant
        with patch("time.sleep"):
            result = self.pagination_manager.navigate_to_page(2)
            self.assertTrue(result)
            self.assertEqual(self.pagination_manager.current_page, 2)

            # Verify link was clicked
            mock_link.click.assert_called_once()

    def test_navigate_to_page_failure(self):
        """Test navigate_to_page with failure."""
        # Mock find_elements to return empty
        self.driver.find_elements.return_value = []

        result = self.pagination_manager.navigate_to_page(2)
        self.assertFalse(result)
        self.assertEqual(self.pagination_manager.current_page, 1)  # Unchanged

    def test_get_total_pages(self):
        """Test get_total_pages with pagination info text."""
        # Mock find_elements to return an element with pagination info
        mock_element = MagicMock()
        mock_element.text = "Page 1 of 5"
        self.driver.find_elements.return_value = [mock_element]

        result = self.pagination_manager.get_total_pages()
        self.assertEqual(result, 5)

    def test_reset(self):
        """Test reset method."""
        self.pagination_manager.current_page = 3
        self.pagination_manager.reset()
        self.assertEqual(self.pagination_manager.current_page, 1)


if __name__ == "__main__":
    unittest.main()
