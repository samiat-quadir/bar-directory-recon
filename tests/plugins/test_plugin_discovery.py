def test_plugin_discovery_imports():
    from universal_recon.plugins import manager
    plugs = manager.load_plugins()
    assert any(getattr(p, "name", "") == "example_plugin" for p in plugs)
