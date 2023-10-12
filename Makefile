.PHONY: help lint test benchmark-prompt-scanners benchmark-output-scanners build docs-serve install-dev publish clean

help:
	@echo "Available commands:"
	@echo "make lint                      - Check code with linters using pre-commit."
	@echo "make test                      - Run unit tests using pytest."
	@echo "make benchmark-prompt-scanners - Benchmark prompt scanners."
	@echo "make benchmark-output-scanners - Benchmark output scanners."
	@echo "make build                     - Build the package for PyPI."
	@echo "make docs-serve                - Serve documentation using mkdocs."
	@echo "make install-dev               - Install development dependencies."
	@echo "make publish                   - Publish to PyPI."

install-dev:
	@echo "Installing development dependencies..."
	@pip install -U -r requirements.txt -r requirements-dev.txt
	@pre-commit install

lint:
	@echo "Running linters..."
	@pre-commit run --all-files

test:
	@echo "Running tests..."
	@pytest --exitfirst --verbose --failed-first --cov=.

benchmark-prompt-scanners:
	@echo "Running benchmarks for prompt scanners..."
	@pytest ./benchmarks/scan_prompt_latency.py

benchmark-output-scanners:
	@echo "Running benchmarks for output scanners..."
	@pytest ./benchmarks/scan_output_latency.py

build:
	@echo "Building for PyPI..."
	@python setup.py sdist bdist_wheel

publish:
	@echo "Publishing to PyPI..."
	@twine upload dist/* --repository llm-guard

docs-serve:
	@echo "Serving documentation..."
	@mkdocs serve -a localhost:8080

clean:
	@echo "Cleaning up..."
	@rm -rf build dist .pytest_cache .egg-info
