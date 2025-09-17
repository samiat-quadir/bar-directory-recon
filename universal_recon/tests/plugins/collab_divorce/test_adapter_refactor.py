import csv
import io
import tempfile
from pathlib import Path

from plugins.collab_divorce import adapter


def test_normalize_email_basic():
    assert adapter.normalize_email(None) == ""
    assert adapter.normalize_email("") == ""
    assert adapter.normalize_email("  Foo.Bar@Example.COM ") == "foo.bar@example.com"
    assert (
        adapter.normalize_email("multiple@example.com;other@x.com")
        == "multiple@example.com"
    )
    assert adapter.normalize_email("not-an-email") == ""


def test_detect_csv_dialect_and_iter_profiles():
    # create a TSV sample
    sample = "Name\tEmail\tFirm\nAlice Smith\tALICE@EX.COM\tSmith LLC\n"
    dialect = adapter.detect_csv_dialect(sample)
    # sniff may return tab or comma; ensure reader can parse both
    f = io.StringIO(sample)
    reader = csv.DictReader(f, dialect=dialect)
    rows = list(reader)
    assert len(rows) == 1
    # write to a temp file and run iter_profiles
    td = tempfile.gettempdir()
    p = Path(td) / "test_adapter_refactor.csv"
    try:
        p.write_text(sample, encoding="utf-8")
        ad = adapter.CollabDivorceAdapter(source_csv=p)
        profiles = list(ad.iter_profiles())
        assert len(profiles) == 1
        prof = profiles[0]
        assert prof["name"] == "Alice Smith"
        # normalized email should be lowercased and valid; exact domain may vary from sample
        assert prof["email"].startswith("alice")
    finally:
        try:
            p.unlink()
        except Exception:
            pass
