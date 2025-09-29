import importlib

import pytest

sl = importlib.import_module("score_leads")


@pytest.mark.parametrize(
    "score,expected",
    [
        (0, "MINIMAL"),
        (24, "MINIMAL"),
        (25, "LOW"),
        (49, "LOW"),
        (50, "MEDIUM"),
        (79, "MEDIUM"),
        (80, "HIGH"),
        (100, "HIGH"),
    ],
)
def test_get_priority_level_boundaries(score, expected):
    scorer = sl.LeadScoringEngine()
    assert hasattr(scorer, "get_priority_level"), "get_priority_level() missing"
    assert scorer.get_priority_level(score) == expected
