import unittest
from plugins import social_link_parser
from utils.record_normalizer import normalize

# Mock WebDriver and context
def mock_driver_with_html(html):
    class MockDriver:
        def __init__(self, html):
            self.page_source = html
            self.current_url = "http://example.com/test"
    return MockDriver(html)

class TestSocialLinkParser(unittest.TestCase):

    def setUp(self):
        with open("snapshots/sample.html", "r", encoding="utf-8") as f:
            self.sample_html = f.read()
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
