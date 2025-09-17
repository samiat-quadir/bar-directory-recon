import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent.parent.parent))


def test_plugin_import():
    from plugins.collab_divorce.adapter import CollabDivorceAdapter

    assert CollabDivorceAdapter is not None


def test_basic_functionality():
    # Test with a simple CSV content
    import tempfile

    from plugins.collab_divorce.adapter import CollabDivorceAdapter

    csv_content = "Name,Email\nJohn Doe,john@example.com\n"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(csv_content)
        csv_path = pathlib.Path(f.name)

    adapter = CollabDivorceAdapter(source_csv=csv_path)
    profiles = list(adapter.iter_profiles())

    assert len(profiles) == 1
    assert profiles[0]["name"] == "John Doe"
    assert profiles[0]["email"] == "john@example.com"
    assert profiles[0]["specialty"] == "Collaborative Divorce"
