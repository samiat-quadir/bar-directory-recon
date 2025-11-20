"""User-facing CLI package for bar-directory-recon."""
from __future__ import annotations

from importlib import metadata

_PACKAGE_NAME = "bar-directory-recon"


def get_version() -> str:
    """Return the installed package version with a safe fallback."""
    try:
        return metadata.version(_PACKAGE_NAME)
    except metadata.PackageNotFoundError:
        # When running from source without an installed wheel we still
        # need a deterministic version string for CLI output.
        return "0.0.0-dev"


__all__ = ["get_version"]
