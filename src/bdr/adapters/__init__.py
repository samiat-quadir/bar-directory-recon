"""Adapters for preserved utilities with safe fallbacks."""
import os

# Import-guarded optional imports
def _load_optional_adapters():
    """Load optional adapters with safe fallbacks."""
    adapters = {}
    
    # Check if we're in safe mode (BDR_SAFE_MODE=1)
    safe_mode = os.environ.get('BDR_SAFE_MODE', '0') == '1'
    
    if safe_mode:
        return adapters
    
    # Try importing optional dependencies
    try:
        import pandas as pd
        adapters['pandas'] = pd
    except ImportError:
        pass
    
    try:
        import numpy as np
        adapters['numpy'] = np
    except ImportError:
        pass
    
    return adapters

# Load adapters on module import
ADAPTERS = _load_optional_adapters()
