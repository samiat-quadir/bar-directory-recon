import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add universal_recon to Python path
universal_recon_path = str(Path(__file__).parent.parent)
if universal_recon_path not in sys.path:
    sys.path.insert(0, universal_recon_path)
