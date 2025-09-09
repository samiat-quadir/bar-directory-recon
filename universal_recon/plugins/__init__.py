"""Plugins module for universal_recon."""

from .firm_parser import parse_firm_data
# Export manager module for tests that import it directly
from . import manager

__all__ = ["parse_firm_data", "manager"]
