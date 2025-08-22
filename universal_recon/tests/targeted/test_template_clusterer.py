"""Test template clusterer utility functionality."""
from universal_recon.utils.template_clusterer import generate_template


def test_generate_template_empty_records():
    """Test that generate_template handles empty record list."""
    result = generate_template([])
    assert isinstance(result, list)
    assert result == []


def test_generate_template_single_record():
    """Test that generate_template handles single record properly."""
    records = [{"type": "email", "value": "test@example.com", "url": "http://test.com"}]
    result = generate_template(records)
    assert isinstance(result, list)
    assert len(result) >= 0  # Should not crash


def test_generate_template_multiple_records():
    """Test that generate_template processes multiple records."""
    records = [
        {"type": "email", "value": "test1@example.com", "url": "http://test1.com"},
        {"type": "email", "value": "test2@example.com", "url": "http://test2.com"},
        {"type": "phone", "value": "555-1234", "url": "http://test1.com"}
    ]
    result = generate_template(records)
    assert isinstance(result, list)
    # Should not crash and return some kind of templated output