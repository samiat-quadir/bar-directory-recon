import importlib
def test_plugin_loader_lists_plugins():
    m = importlib.import_module('universal_recon.plugin_loader')
    # Test that we can load plugins by type
    plugins = m.load_plugins_by_type("test")
    # Should return empty list but not error
    assert isinstance(plugins, list)
