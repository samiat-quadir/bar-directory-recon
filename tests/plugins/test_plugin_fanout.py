def test_plugin_fanout_yields_record():
    from universal_recon.plugins import manager

    out = list(manager.fanout({"q": "smoke"}))
    assert any(record.get("example") is True for record in out)
