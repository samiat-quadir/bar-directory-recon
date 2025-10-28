def test_metrics_flag_loads():
    import os, importlib
    os.environ['BDR_ADAPTER_METRICS']='1'
    m = importlib.import_module('bdr.metrics')
    assert hasattr(m,'enable') and hasattr(m,'snapshot')