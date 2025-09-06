def test_plugin_fanout_yields_record():
    from universal_recon.plugins import manager
    out = list(manager.fanout({"q":"smoke"}))
    assert out and out[0].get("example") is True
