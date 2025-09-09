#!/usr/bin/env python3
"""
Tests for the HallandalePropertyProcessor in pdf_processor module.
"""

import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

import pandas as pd

from src.pdf_processor import HallandalePropertyProcessor


class TestHallandalePropertyProcessor(unittest.TestCase):
    """Test cases for the HallandalePropertyProcessor class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a processor with a temp directory
        with patch.object(Path, "mkdir") as mock_mkdir:
            self.processor = HallandalePropertyProcessor(output_dir="temp_test_outputs")
            mock_mkdir.assert_called_once()

    @patch("logging.FileHandler")
    @patch("logging.StreamHandler")
    @patch("logging.basicConfig")
    def test_setup_logging(
        self, mock_basic_config, mock_stream_handler, mock_file_handler
    ):
        """Test that logging is configured correctly."""
        self.processor._setup_logging()
        mock_basic_config.assert_called_once()

        # Verify both handlers are used
        args, _ = mock_basic_config.call_args
        kwargs = mock_basic_config.call_args.kwargs
        self.assertEqual(kwargs["level"], unittest.mock.ANY)
        self.assertEqual(len(kwargs["handlers"]), 2)

    @patch("builtins.open", new_callable=mock_open)
    @patch("pandas.DataFrame.to_csv")
    def test_create_sample_data(self, mock_to_csv, mock_open):
        """Test creation of sample data."""
        sample_properties = self.processor._create_sample_data()

        # Verify sample data has expected structure
        self.assertEqual(len(sample_properties), 20)

        # Check a sample property has all expected fields
        first_prop = sample_properties[0]
        self.assertIn("property_address", first_prop)
        self.assertIn("owner_name", first_prop)
        self.assertIn("mailing_address", first_prop)
        self.assertIn("year_built", first_prop)
        self.assertIn("folio_number", first_prop)
        self.assertIn("inspection_due", first_prop)
        self.assertIn("notes", first_prop)

    def test_clean_text(self):
        """Test text cleaning functionality."""
        # Test various text cleaning scenarios
        self.assertEqual(self.processor._clean_text(" Test  Text "), "Test Text")
        self.assertEqual(self.processor._clean_text(None), "")
        self.assertEqual(self.processor._clean_text("null"), "")
        self.assertEqual(self.processor._clean_text("N/A"), "")

        # Test with pandas NA
        self.assertEqual(self.processor._clean_text(pd.NA), "")

    def test_standardize_address(self):
        """Test address standardization."""
        # Test common address transformations
        self.assertEqual(
            self.processor._standardize_address("123 Main Street"), "123 MAIN ST"
        )
        self.assertEqual(
            self.processor._standardize_address("456 Oak Avenue"), "456 OAK AVE"
        )
        self.assertEqual(
            self.processor._standardize_address("789 Pine Boulevard"), "789 PINE BLVD"
        )

    def test_standardize_year(self):
        """Test year standardization."""
        # Test extraction of years from various formats
        self.assertEqual(self.processor._standardize_year("Built in 1985"), "1985")
        self.assertEqual(self.processor._standardize_year("2010"), "2010")
        self.assertEqual(self.processor._standardize_year("Constructed: 1995"), "1995")
        self.assertEqual(
            self.processor._standardize_year("Unknown"), "Unknown"
        )  # No year to extract

    def test_deduplicate_properties(self):
        """Test property deduplication."""
        # Create sample properties with some duplicates
        properties = [
            {"property_address": "123 Main St", "owner_name": "John Doe"},
            {"property_address": "456 Oak Ave", "owner_name": "Jane Smith"},
            {
                "property_address": "123 MAIN ST",
                "owner_name": "Different Owner",
            },  # Duplicate with different case
            {"property_address": "789 Pine Blvd", "owner_name": "Another Owner"},
        ]

        unique_properties = self.processor._deduplicate_properties(properties)

        # Should only have 3 unique addresses (123 MAIN ST is a duplicate)
        self.assertEqual(len(unique_properties), 3)

        # The first instance of each address should be kept
        self.assertEqual(unique_properties[0]["owner_name"], "John Doe")

    @patch("os.path.exists")
    @patch("pandas.DataFrame.to_csv")
    def test_process_pdf_file_not_found(self, mock_to_csv, mock_exists):
        """Test process_pdf with non-existent file."""
        # Mock Path.exists to return False
        mock_exists.return_value = False

        result = self.processor.process_pdf("nonexistent.pdf")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "PDF file not found")

    @patch("pathlib.Path.exists")
    @patch("src.pdf_processor.pdfplumber", None)  # Simulate unavailable pdfplumber
    @patch("src.pdf_processor.tabula", None)  # Simulate unavailable tabula
    @patch("src.pdf_processor.PyPDF2", None)  # Simulate unavailable PyPDF2
    @patch("pandas.DataFrame.to_csv")
    def test_process_pdf_fallback_to_sample(self, mock_to_csv, mock_exists):
        """Test process_pdf falling back to sample data when no extractors available."""
        # Mock Path.exists to return True
        mock_exists.return_value = True

        # Patch the PDF_PLUMBER_AVAILABLE and other constants
        with (
            patch("src.pdf_processor.PDF_PLUMBER_AVAILABLE", False),
            patch("src.pdf_processor.TABULA_AVAILABLE", False),
            patch("src.pdf_processor.PYPDF2_AVAILABLE", False),
            patch.object(self.processor, "_create_sample_data") as mock_sample,
        ):

            # Mock the sample data creation
            mock_sample.return_value = [{"property_address": "Sample Address"}]

            result = self.processor.process_pdf("test.pdf")

            # Verify it falls back to sample data
            self.assertEqual(result["status"], "success")
            mock_sample.assert_called_once()
            mock_to_csv.assert_called_once()

    def test_parse_table_row(self):
        """Test parsing of table rows."""
        # Test with complete row data
        row = [
            "123 Main St",
            "John Doe",
            "456 Oak Ave",
            "1985",
            "12345",
            "2025-01-01",
            "Notes here",
        ]
        result = self.processor._parse_table_row(row)

        self.assertEqual(result["property_address"], "123 Main St")
        self.assertEqual(result["owner_name"], "John Doe")
        self.assertEqual(result["year_built"], "1985")

        # Test with partial row data
        row = ["123 Main St", "John Doe"]
        result = self.processor._parse_table_row(row)

        self.assertEqual(result["property_address"], "123 Main St")
        self.assertEqual(result["owner_name"], "John Doe")
        self.assertEqual(result["mailing_address"], "")  # Default empty string

        # Test with empty property address
        row = ["", "John Doe"]
        result = self.processor._parse_table_row(row)

        self.assertIsNone(result)  # Should return None if no property address

    def test_is_address_line(self):
        """Test address line detection."""
        # Test various address formats
        self.assertTrue(self.processor._is_address_line("123 Main St"))
        self.assertTrue(
            self.processor._is_address_line("456 NE 2nd Ave, Hallandale Beach, FL")
        )
        self.assertTrue(self.processor._is_address_line("789 SW 3rd Rd"))

        # Test non-address text
        self.assertFalse(self.processor._is_address_line("John Smith"))
        self.assertFalse(self.processor._is_address_line("Property Information"))
        self.assertFalse(self.processor._is_address_line("Year Built: 1985"))

    def test_split_line_into_parts(self):
        """Test line splitting logic."""
        # Test with tab delimiter
        line = "123 Main St\tJohn Doe\t1985"
        parts = self.processor._split_line_into_parts(line)
        self.assertEqual(parts, ["123 Main St", "John Doe", "1985"])

        # Test with double space delimiter
        line = "123 Main St  John Doe  1985"
        parts = self.processor._split_line_into_parts(line)
        self.assertEqual(parts, ["123 Main St", "John Doe", "1985"])

        # Test with comma delimiter
        line = "123 Main St, John Doe, 1985"
        parts = self.processor._split_line_into_parts(line)
        self.assertEqual(parts, ["123 Main St", "John Doe", "1985"])


if __name__ == "__main__":
    unittest.main()
