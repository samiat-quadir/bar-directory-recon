#!/usr/bin/env bash
set -Eeuo pipefail
cd "/workspaces/bar-directory-recon"
python -V
# keep it minimal; ensure pytest is present then run a tiny target
if ! command -v pytest >/dev/null 2>&1; then python -m pip install -q pytest; fi
pytest -q universal_recon/tests/plugins/collab_divorce/test_adapter_offline.py -k "." || exit $?
