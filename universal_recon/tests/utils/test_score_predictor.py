# tests/utils/test_score_predictor.py

import unittest
from utils import score_predictor

class TestScorePredictor(unittest.TestCase):

    def setUp(self):
        self.records = [
            {"type": "email", "value": "john@example.com"},
            {"type": "phone", "value": "555-1234"},
            {"type": "firm_name", "value": "Jackson & Co."},
            {"type": "bar_number", "value": "BRX-009876"},
            {"type": "other", "value": "Misc info"},
            {"type": "email", "value": "x@"},  # likely invalid
        ]

    def test_prediction_keys_added(self):
        results = score_predictor.predict_scores(self.records)
        for r in results:
            self.assertIn("predicted_score", r)
            self.assertIn("predicted_confidence", r)

    def test_confidence_mapping(self):
        results = score_predictor.predict_scores(self.records)
        for r in results:
            confidence = r["predicted_confidence"]
            self.assertIn(confidence, ["low", "medium", "high"])
            self.assertIsInstance(r["predicted_score"], float)

    def test_score_range(self):
        results = score_predictor.predict_scores(self.records)
        for r in results:
            self.assertGreaterEqual(r["predicted_score"], 0.0)
            self.assertLessEqual(r["predicted_score"], 1.0)

if __name__ == "__main__":
    unittest.main()
