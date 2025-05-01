import unittest

from utils.recon_trend_tracker import analyze_trends

mock_summary_past = {
    "site": "test_site",
    "total_records": 10,
    "valid_count": 8,
    "invalid_count": 2,
    "top_fields": {"email": 5, "firm_name": 4, "phone": 3},
    "rank_distribution": {"1": 2, "2": 2, "3": 3, "4": 2, "5": 1},
    "plugin_usage": {"email_plugin": 6, "firm_parser": 4},
}

mock_summary_current = {
    "site": "test_site",
    "total_records": 9,
    "valid_count": 6,
    "invalid_count": 3,
    "top_fields": {"email": 3, "firm_name": 2, "phone": 1},
    "rank_distribution": {"1": 3, "2": 1, "3": 2, "4": 2, "5": 1},
    "plugin_usage": {"email_plugin": 3, "firm_parser": 2},
}


class TestReconTrendTracker(unittest.TestCase):

    def test_analyze_trends_output_shape(self):
        result = analyze_trends("test_site", [mock_summary_past, mock_summary_current])
        self.assertIn("field_score_drift", result)
        self.assertIn("plugin_activity_drift", result)
        self.assertIn("field_absence_trends", result)

    def test_detect_field_score_drop(self):
        result = analyze_trends("test_site", [mock_summary_past, mock_summary_current])
        self.assertGreater(result["field_score_drift"]["email"], 0)
        self.assertGreater(result["field_score_drift"]["firm_name"], 0)

    def test_detect_plugin_usage_drop(self):
        result = analyze_trends("test_site", [mock_summary_past, mock_summary_current])
        self.assertIn("email_plugin", result["plugin_activity_drift"])
        self.assertGreater(result["plugin_activity_drift"]["email_plugin"], 0)

    def test_field_absence_trend_detected(self):
        result = analyze_trends("test_site", [mock_summary_past, mock_summary_current])
        self.assertIn("phone", result["field_absence_trends"])


if __name__ == "__main__":
    unittest.main()
