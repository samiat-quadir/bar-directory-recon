from universal_recon.util.secrets import get_secret


def test_secret_absent_returns_none(monkeypatch):
    monkeypatch.delenv("SCRAPER_API_KEY", raising=False)
    assert get_secret("SCRAPER_API_KEY") is None


def test_secret_present_is_read(monkeypatch):
    monkeypatch.setenv("SCRAPER_API_KEY", "TEST_VALUE")
    assert get_secret("SCRAPER_API_KEY") == "TEST_VALUE"
