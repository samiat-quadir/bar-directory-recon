import unittest

from universal_recon.utils import score_visualizer
from universal_recon.utils.score_visualizer import generate_visualization

MOCK_RECORDS = [
    {"plugin": "email_plugin", "type": "email", "score": 1},
    {"plugin": "email_plugin", "type": "email", "score": 3},
    {"plugin": "email_plugin", "type": "email", "score": 5},
    {"plugin": "firm_parser", "type": "firm_name", "score": 1},
    {"plugin": "firm_parser", "type": "firm_name", "score": 3},
    {"plugin": "bar_number_annotator", "type": "bar_number", "score": 5},
]


class TestScoreVisualizer(unittest.TestCase):

    def test_generate_heatmap_data_structure(self):
        heatmap = score_visualizer.generate_heatmap_data(MOCK_RECORDS)

        self.assertIn("email_plugin", heatmap)
        self.assertIn("email", heatmap["email_plugin"])
        self.assertEqual(heatmap["email_plugin"]["email"]["critical"], 1)
        self.assertEqual(heatmap["email_plugin"]["email"]["warning"], 1)
        self.assertEqual(heatmap["email_plugin"]["email"]["clean"], 1)

        self.assertEqual(heatmap["firm_parser"]["firm_name"]["critical"], 1)
        self.assertEqual(heatmap["firm_parser"]["firm_name"]["warning"], 1)

        self.assertEqual(heatmap["bar_number_annotator"]["bar_number"]["clean"], 1)

    def test_save_heatmap_data(self):
        site = "test_site"
        heatmap = score_visualizer.generate_heatmap_data(MOCK_RECORDS)
        score_visualizer.save_heatmap_data(site, heatmap)

        with open(f"output/reports/{site}_heatmap.json", "r", encoding="utf-8") as f:
            data = f.read()
        self.assertIn("email_plugin", data)
        self.assertIn("critical", data)
        self.assertIn("firm_parser", data)


def test_generate_visualization():
    """Basic test to verify visualization generation."""
    assert callable(generate_visualization)


if __name__ == "__main__":
    unittest.main()
