#!/usr/bin/env python3
"""
Check development and testing tools
"""

def check_dev_tools():
    """Check development tools availability."""
    dev_tools = [
        ('pytest', 'pytest'),
        ('black', 'black'),
        ('isort', 'isort'),
        ('mypy', 'mypy'),
        ('flake8', 'flake8'),
        ('bandit', 'bandit'),
        ('pre-commit', 'pre_commit'),
        ('lxml', 'lxml'),
        ('pillow', 'PIL'),
        ('schedule', 'schedule'),
    ]

    missing = []
    available = []

    for tool_name, import_name in dev_tools:
        try:
            __import__(import_name)
            print(f'✅ {tool_name} - Available')
            available.append(tool_name)
        except ImportError:
            print(f'⚠️  {tool_name} - Not installed')
            missing.append(tool_name)

    print(f"\n📊 Summary: {len(available)} available, {len(missing)} missing")

    if missing:
        print(f'\n📦 Install missing tools:')
        print(f'pip install {" ".join(missing)}')
    else:
        print('\n🎉 All development tools available!')

    return missing

if __name__ == "__main__":
    check_dev_tools()
