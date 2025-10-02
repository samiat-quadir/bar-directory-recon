"""Plugins module for universal_recon."""

# Export manager module for tests that import it directly
from . import manager
from .firm_parser import parse_firm_data

__all__ = ["parse_firm_data", "manager"]
