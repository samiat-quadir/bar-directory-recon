#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || echo .)"
python -V || true
# Run a conservative smoke: no cacheprovider, no inherited addopts
pytest -p no:cacheprovider -o addopts="" -q --maxfail=1 universal_recon/tests tests -k "not slow and not e2e and not integration"
