import pytest

# Skip this test if the example plugin package isn't available. The plugin
# scaffold lives on a separate PR/branch; main should not fail because of it.
pytest.importorskip(
    "universal_recon.plugins.example_plugin",
    reason="example plugin scaffold not present on main",
)


def test_example_plugin_smoke():
    # A minimal smoke test exercising the plugin API surface that will be
    # present when the scaffold PR is merged. Keep assertions minimal to
    # avoid coupling to implementation details.
    from universal_recon.plugins import example_plugin

    assert hasattr(example_plugin, "initialize")
    assert callable(getattr(example_plugin, "initialize"))
