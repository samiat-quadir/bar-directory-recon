import contextlib
import importlib
import os


@contextlib.contextmanager
def safe_env():
    # Reduce chance of heavy side-effects during import
    os.environ.setdefault("CI", "1")
    os.environ.setdefault("DRY_RUN", "1")
    yield


def _import(modname: str):
    with safe_env():
        importlib.invalidate_caches()
        importlib.import_module(modname)


def test_import_async_pipeline_demo():
    _import("async_pipeline_demo")


def test_import_check_enhancements():
    _import("check_enhancements")


def test_import_complete_installation_check():
    _import("complete_installation_check")


def test_import_complete_verification():
    _import("complete_verification")


def test_import_setup_check():
    _import("setup_check")


def test_import_universal_automation():
    _import("universal_automation")

def test_import_usage_demo():
    _import("usage_demo")


def test_import_universal_recon_plugins_loader():
    _import("universal_recon.plugins.loader")


def test_import_universal_recon_plugins_reference_realtor():
    _import("universal_recon.plugins.reference_realtor")


def test_import_universal_recon_plugins_social_link_parser():
    _import("universal_recon.plugins.social_link_parser")

