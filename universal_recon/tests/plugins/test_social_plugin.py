import importlib


def test_social_plugin_loads():
    m = importlib.import_module('universal_recon.plugins.social_link_parser_plugin')
    assert hasattr(m, 'SocialLinkParserPlugin')


def test_social_plugin_contract_smoke(monkeypatch):
    m = importlib.import_module('universal_recon.plugins.social_link_parser_plugin')
    P = m.SocialLinkParserPlugin()
    base = importlib.import_module('universal_recon.plugins.social_link_parser')
    if not hasattr(base, 'iter_profiles'):
        P.fetch = lambda **_: iter([{"profile_url": "https://x.com/acme", "raw": {}}])
    outs = []
    for rec in P.fetch():
        assert isinstance(rec, dict)
        if P.validate(rec):
            outs.append(P.transform(rec))
    assert outs and isinstance(outs[0], dict)
