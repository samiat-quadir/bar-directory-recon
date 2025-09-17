import importlib


def test_firm_plugin_loads():
    m = importlib.import_module("universal_recon.plugins.firm_parser")
    assert hasattr(m, "FirmParserPlugin")


def test_firm_plugin_contract_smoke(monkeypatch):
    m = importlib.import_module("universal_recon.plugins.firm_parser")
    P = m.FirmParserPlugin()

    # If the real underlying functions are absent in CI, stub a minimal iterator
    base = importlib.import_module("universal_recon.plugins.firm_parser")
    if not hasattr(base, "iter_firms"):
        P.fetch = lambda **_: iter([{"name": "Acme", "industry": "Legal Services", "raw": {}}])

    outs = []
    for rec in P.fetch():
        assert isinstance(rec, dict)
        transformed = P.transform(rec)
        if P.validate(transformed):
            outs.append(transformed)
    assert outs and isinstance(outs[0], dict)
