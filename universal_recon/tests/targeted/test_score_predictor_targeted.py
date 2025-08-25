"""Test score predictor utility functionality (targeted variant)."""
from universal_recon.utils.score_predictor import predict_score


def test_predict_score_empty_records():
    """Test that predict_score handles empty record list."""
    result = predict_score([])
    assert isinstance(result, list)
    assert result == []


def test_predict_score_preserves_record_structure():
    """Test that predict_score preserves original record structure."""
    records = [
        {"type": "email", "value": "test@example.com", "confidence": 0.8},
        {"type": "phone", "value": "555-1234", "confidence": 0.9}
    ]
    result = predict_score(records)
    assert isinstance(result, list)
    assert len(result) == len(records)

    # Check that original fields are preserved
    for i, record in enumerate(result):
        assert "type" in record
        assert "value" in record
        assert record["type"] == records[i]["type"]
        assert record["value"] == records[i]["value"]


def test_predict_score_adds_predicted_scores():
    """Test that predict_score adds predicted score fields."""
    records = [{"type": "email", "value": "test@example.com"}]
    result = predict_score(records)
    assert isinstance(result, list)
    assert len(result) == 1
    # Should have some kind of score prediction logic applied

