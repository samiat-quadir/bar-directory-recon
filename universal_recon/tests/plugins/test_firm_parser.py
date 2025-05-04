import unittest

<<<<<<< HEAD
from universal_recon.plugins import firm_parser

# Import from proper package path
from universal_recon.utils.record_normalizer import normalize

=======
from utils.record_normalizer import normalize
>>>>>>> bf5b0be (🧽 Fix all Flake8 + formatting issues across universal_recon/)

from plugins import firm_parser

# Mock WebDriver and context
<<<<<<< HEAD
=======


>>>>>>> bf5b0be (🧽 Fix all Flake8 + formatting issues across universal_recon/)
def mock_driver_with_html(html):
    class MockDriver:
        def __init__(self, html):
            self.page_source = html
            self.current_url = "http://example.com/test"

    return MockDriver(html)


class TestFirmParserPlugin(unittest.TestCase):
    def setUp(self):
        with open("snapshots/sample.html", "r", encoding="utf-8") as f:
            self.sample_html = f.read()
        self.driver = mock_driver_with_html(self.sample_html)

    def test_plugin_output_soft_mode(self):
        records = firm_parser.apply(self.driver, context="test_soft")
        normalized = normalize(records, strict=False)
        self.assertIsInstance(normalized, list)
        for record in normalized:
            self.assertEqual(record.get("type"), "firm_name")
            self.assertIn("value", record)
            self.assertIn("url", record)
            self.assertIn("confidence", record)
            self.assertGreaterEqual(record["confidence"], 0.0)
            self.assertLessEqual(record["confidence"], 1.0)

    def test_plugin_output_strict_mode(self):
        records = firm_parser.apply(self.driver, context="test_strict")
        try:
            # Store the result and assert it's a list to verify normalization succeeded
            normalized = normalize(records, strict=True)
            self.assertIsInstance(normalized, list)
        except Exception as e:
            self.fail(f"Strict normalization failed: {e}")


if __name__ == "__main__":
    unittest.main()
