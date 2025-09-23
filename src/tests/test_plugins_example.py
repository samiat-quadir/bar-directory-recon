from universal_recon.plugins.example_plugin import ExamplePlugin


def test_example_plugin_runs():
    p = ExamplePlugin()
    out = p.run({"a": 1})
    assert out["name"] == "example"
    assert "a" in out["received_keys"]
