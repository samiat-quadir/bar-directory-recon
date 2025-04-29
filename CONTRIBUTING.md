# Contributing to Bar Directory Recon

## Development Setup

1. Clone the repository and create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Unix
.venv\Scripts\activate    # Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install pre-commit hooks:

```bash
pre-commit install
```

## Code Quality Standards

We use several tools to maintain code quality:

- **Black**: Code formatting (100 character line length)
- **isort**: Import sorting
- **flake8**: Style guide enforcement
- **mypy**: Static type checking
- **bandit**: Security checks
- **pytest**: Unit testing

These checks run automatically on commit via pre-commit hooks.

## Development Workflow

1. Create a new branch for your feature/fix:

```bash
git checkout -b feature/your-feature-name
```

2. Make your changes, following our coding standards:
   - Add type hints to new functions
   - Write docstrings for modules, classes, and functions
   - Include tests for new functionality
   - Update documentation as needed

3. Run tests locally:

```bash
pytest
```

4. Check test coverage:

```bash
pytest --cov=src --cov=universal_recon --cov-report=html
```

5. Commit your changes using conventional commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `refactor:` for code refactoring
   - `test:` for adding tests
   - `chore:` for maintenance tasks

## Docker Development

For Docker-based development:

1. Build the image:

```bash
docker-compose build
```

2. Run with standard configuration:

```bash
docker-compose up
```

3. Run with debug configuration:

```bash
docker-compose -f docker-compose.debug.yml up
```

Debug port 5678 is exposed for VS Code Python debugger integration.

## VS Code Integration

We provide preconfigured VS Code tasks for common operations:

1. Press `Ctrl+Shift+P` and select "Tasks: Run Task"
2. Choose from:
   - "Security Check": Run Bandit security scan
   - "Dependency Check": Check dependencies for vulnerabilities
   - "Run Tests": Execute test suite with coverage report

## Continuous Integration

Our GitHub Actions workflows automatically:

1. Run tests on Python 3.12 and 3.13
2. Check code quality and security
3. Build and test Docker images
4. Generate coverage reports
5. Scan dependencies for vulnerabilities

## Need Help?

- Check the [README.md](README.md) for project overview
- Review [docs/](docs/) for detailed documentation
- Create an issue for bugs or feature requests
- Reach out to maintainers for guidance

## License

By contributing, you agree that your contributions will be licensed under the project's MIT license.
