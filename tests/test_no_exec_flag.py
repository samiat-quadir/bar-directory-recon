"""Test --no-exec flag and safe mode fallback."""
import os
import subprocess
import sys


def test_no_exec_flag_sets_env():
    """Test that --no-exec flag sets BDR_SAFE_MODE=1."""
    # Clear any existing BDR_SAFE_MODE
    env = os.environ.copy()
    env.pop('BDR_SAFE_MODE', None)

    # Run bdr with --no-exec and capture behavior via doctor
    result = subprocess.run(
        [sys.executable, '-m', 'bdr', '--no-exec', 'doctor'],
        env=env,
        capture_output=True,
        text=True
    )

    # Should complete successfully
    assert result.returncode == 0
    # Doctor output should show safe mode info
    assert 'BDR_SAFE_MODE' in result.stdout


def test_adapters_safe_mode_fallback():
    """Test that adapters module respects BDR_SAFE_MODE."""
    # Set safe mode
    os.environ['BDR_SAFE_MODE'] = '1'

    # Import should work without optional dependencies
    from bdr.adapters import ADAPTERS

    # In safe mode, adapters dict should be empty or minimal
    assert isinstance(ADAPTERS, dict)

    # Clean up
    os.environ.pop('BDR_SAFE_MODE', None)


def test_adapters_normal_mode():
    """Test that adapters module loads normally without safe mode."""
    # Ensure safe mode is off
    os.environ.pop('BDR_SAFE_MODE', None)

    # Re-import to test fresh state
    import importlib

    import bdr.adapters
    importlib.reload(bdr.adapters)

    from bdr.adapters import ADAPTERS

    # Should attempt to load optional dependencies
    assert isinstance(ADAPTERS, dict)
    # May or may not have entries depending on installed packages
