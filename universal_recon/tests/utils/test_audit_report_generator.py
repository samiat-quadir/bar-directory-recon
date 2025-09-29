import unittest

from universal_recon.utils.audit_report_generator import generate_audit_report


class TestAuditReportGenerator(unittest.TestCase):
    def setUp(self):
        self.sample_records = [
            {
                "type": "email",
                "value": "valid@example.com",
                "plugin": "email_plugin",
                "score": 5,
            },
            {"type": "email", "value": "", "plugin": "email_plugin", "score": 1},
            {
                "type": "firm_name",
                "value": "Test LLP",
                "plugin": "firm_parser",
                "score": 4,
            },
            {"type": "firm_name", "value": "", "plugin": "firm_parser", "score": 0},
            {
                "type": "bar_number",
                "value": "1234",
                "plugin": "bar_number_annotator",
                "score": 2,
            },
            {
                "type": "phone",
                "value": "555-123",
                "plugin": "social_link_parser",
                "score": 5,
            },
        ]

    def test_generate_audit_report_structure(self):
        audit = generate_audit_report(self.sample_records)

        self.assertIn("total_records", audit)
        self.assertIn("score_tiers", audit)
        self.assertIn("validator_errors_by_plugin", audit)
        self.assertEqual(audit["total_records"], len(self.sample_records))

    def test_score_tier_counts(self):
        audit = generate_audit_report(self.sample_records)
        self.assertEqual(audit["score_tiers"]["critical"], 2)
        self.assertEqual(audit["score_tiers"]["warning"], 1)
        self.assertEqual(audit["score_tiers"]["clean"], 3)

    def test_plugin_grouping(self):
        audit = generate_audit_report(self.sample_records)
        self.assertIn("email_plugin", audit["validator_errors_by_plugin"])
        self.assertIn("firm_parser", audit["validator_errors_by_plugin"])
        self.assertGreaterEqual(
            sum(audit["score_tiers"].values()), audit["total_records"]
        )


def test_generate_audit_report():
    """Basic test to verify audit report generation."""
    assert callable(generate_audit_report)


if __name__ == "__main__":
    unittest.main()
