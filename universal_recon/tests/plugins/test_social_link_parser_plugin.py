"""Plugin-style tests for social link parser to avoid import name collision with targeted tests."""

import unittest

from universal_recon.plugins import social_link_parser
from universal_recon.utils.record_normalizer import normalize


# Mock WebDriver and context
def mock_driver_with_html(html):
    class MockDriver:
        def __init__(self, html):
            self.page_source = html
            self.current_url = "http://example.com/test"

    return MockDriver(html)


class TestSocialLinkParserPlugin(unittest.TestCase):
    def setUp(self):
        # snapshot file relative to tests/plugins
        sample_path = "snapshots/sample.html"
        try:
            with open(sample_path, encoding="utf-8") as f:
                self.sample_html = f.read()
        except FileNotFoundError:
            # Fallback minimal HTML if snapshot is missing
            self.sample_html = (
                '<html><body><a href="https://linkedin.com/in/testuser">LinkedIn</a></body></html>'
            )
        self.driver = mock_driver_with_html(self.sample_html)

    def test_social_links_soft_mode(self):
        records = social_link_parser.apply(self.driver, context="test_soft")
        normalized = normalize(records, strict=False)
        self.assertIsInstance(normalized, list)
        for record in normalized:
            self.assertIn("type", record)
            self.assertEqual(record["type"], "social")
            self.assertIn("value", record)
            self.assertIn("url", record)
            self.assertIn("confidence", record)
            self.assertGreaterEqual(record["confidence"], 0.0)
            self.assertLessEqual(record["confidence"], 1.0)

    def test_social_links_strict_mode(self):
        records = social_link_parser.apply(self.driver, context="test_strict")
        try:
            normalized = normalize(records, strict=True)
        except Exception as e:
            self.fail(f"Strict normalization failed: {e}")


if __name__ == "__main__":
    unittest.main()
