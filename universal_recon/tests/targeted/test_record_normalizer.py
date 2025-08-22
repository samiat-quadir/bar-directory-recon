"""Test record normalizer utility functions."""
from universal_recon.utils.record_normalizer import normalize


def test_normalize_adds_optional_defaults():
    """Test that normalize adds default values for optional fields."""
    records = [
        {
            "type": "email",
            "value": "test@example.com",
            "xpath": "//a",
            "context": "root",
            "url": "http://test.com"
        }
    ]
    result = normalize(records)
    
    assert len(result) == 1
    assert result[0]["confidence"] == 1.0
    assert result[0]["source"] == "unknown"
    assert result[0]["category"] is None


def test_normalize_preserves_existing_optional_fields():
    """Test that normalize preserves existing optional field values."""
    records = [
        {
            "type": "email",
            "value": "test@example.com",
            "xpath": "//a",
            "context": "root",
            "url": "http://test.com",
            "confidence": 0.8,
            "source": "custom"
        }
    ]
    result = normalize(records)
    
    assert len(result) == 1
    assert result[0]["confidence"] == 0.8
    assert result[0]["source"] == "custom"


def test_normalize_strict_mode_raises_on_missing_fields():
    """Test that strict mode raises ValueError for missing required fields."""
    records = [{"type": "email", "value": "test@example.com"}]  # missing xpath, context, url
    
    try:
        normalize(records, strict=True)
        assert False, "Expected ValueError to be raised"
    except ValueError as e:
        assert "missing fields" in str(e)


def test_normalize_non_strict_mode_handles_missing_fields():
    """Test that non-strict mode handles missing required fields gracefully."""
    records = [{"type": "email", "value": "test@example.com"}]  # missing xpath, context, url
    result = normalize(records, strict=False)
    
    assert len(result) == 1
    assert result[0]["confidence"] == 1.0
    assert result[0]["source"] == "unknown"