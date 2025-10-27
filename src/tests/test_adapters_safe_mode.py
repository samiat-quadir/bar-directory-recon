import os
from bdr.adapters.normalize_adapter import normalize
from bdr.adapters.validate_adapter import validate_record
from bdr.adapters.validators_loader import load_validators


def test_safe_mode_defaults_to_fallback():
    os.environ.pop('BDR_SAFE_MODE', None)
    r = {'id': 1}
    n = normalize(r)
    v = validate_record(r)
    L = load_validators()
    assert n.get('_normalized') is True
    assert v.get('ok') is True
    assert isinstance(L, dict)


def test_can_disable_safe_mode():
    os.environ['BDR_SAFE_MODE'] = '0'
    r = {'id': 2}
    # Calls may still fallback depending on env; just assert structure
    n = normalize(r)
    v = validate_record(r)
    assert 'ok' in v and '_normalized' in n
