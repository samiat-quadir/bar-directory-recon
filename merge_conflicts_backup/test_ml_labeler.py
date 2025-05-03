import unittest

from universal_recon.plugins import ml_labeler

# Import from proper package path
from universal_recon.utils.record_normalizer import normalize


# Mock WebDriver and context
def mock_driver_with_html(html):
    class MockDriver:
        def __init__(self, html):
            self.page_source = html
            self.current_url = "http://example.com/test"

    return MockDriver(html)


class TestMLLabelerPlugin(unittest.TestCase):
    def setUp(self):
        with open("snapshots/sample.html", "r", encoding="utf-8") as f:
            self.sample_html = f.read()
        self.driver = mock_driver_with_html(self.sample_html)

    def test_plugin_output_soft_mode(self):
        records = ml_labeler.apply(self.driver, context="test_soft")
        normalized = normalize(records, strict=False)
        self.assertIsInstance(normalized, list)
        for record in normalized:
            self.assertIn("type", record)
            self.assertIn("value", record)
            self.assertIn("url", record)
            self.assertIn("confidence", record)
            self.assertGreaterEqual(record["confidence"], 0.0)
            self.assertLessEqual(record["confidence"], 1.0)

    def test_plugin_output_strict_mode(self):
        records = ml_labeler.apply(self.driver, context="test_strict")
        try:
            # Store the result and assert it's a list to verify normalization succeeded
            normalized = normalize(records, strict=True)
            self.assertIsInstance(normalized, list)
        except Exception as e:
            self.fail(f"Strict normalization failed: {e}")


if __name__ == "__main__":
    unittest.main()
