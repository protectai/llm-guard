.PHONY: help lint test build docs-serve install-dev publish clean

help:
	@echo "Available commands:"
	@echo "make lint                      - Check code with linters using pre-commit."
	@echo "make test                      - Run unit tests using pytest."
	@echo "make build                     - Build the package for PyPI."
	@echo "make docs-serve                - Serve documentation using mkdocs."
	@echo "make install-dev               - Install development dependencies."
	@echo "make publish                   - Publish to PyPI."

install-dev:
	@echo "Installing development dependencies..."
	@python -m pip install ".[dev]"
	@python -m pre-commit install

lint:
	@echo "Running linters..."
	@pre-commit run --all-files

test:
	@echo "Running tests..."
	@pytest --exitfirst --verbose --failed-first --cov=.

build:
	@echo "Building for PyPI..."
	@python -m pip install --upgrade build
	@python -m build

publish:
	@echo "Publishing to PyPI..."
	@python -m pip install --upgrade twine
	@python -m twine upload --repository llm-guard dist/*

docs-serve:
	@echo "Serving documentation..."
	@mkdocs serve -a localhost:8085

clean:
	@echo "Cleaning up..."
	@rm -rf build dist .pytest_cache .egg-info
