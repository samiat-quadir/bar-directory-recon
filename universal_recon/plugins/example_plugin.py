"""Example plugin stub used by tests.

Provides a module-level `name` used by the discovery test and a minimal
ExamplePlugin class so the module can be imported safely in CI.
"""

# Name expected by tests that scan discovered plugin modules
name = "example_plugin"


class ExamplePlugin:
    """Minimal stub so test_plugins_example.py can import without errors."""

    def run(self, *args, **kwargs):
        return None


def initialize(*args, **kwargs):
    """Lightweight initialize hook expected by the smoke test.

    Keep the function intentionally minimal so the example plugin remains
    a no-op scaffold that doesn't require external dependencies.
    """
    return None
