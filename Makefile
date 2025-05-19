.DEFAULT_GOAL := help

.PHONY: install-dev
install-dev: ## Install development dependencies.
	@echo "Installing development dependencies..."
	@python -m pip install ".[dev, onnxruntime]" -U
	@pre-commit install

.PHONY: lint
lint: ## Check code with linters using pre-commit.
	@echo "Running linters..."
	@pre-commit run --all-files

.PHONY: test
test: ## Run unit tests using pytest.
	@echo "Running tests..."
	@pytest --exitfirst --verbose --failed-first --cov=.

.PHONY: build
build: ## Build the package for PyPI.
	@echo "Building for PyPI..."
	@python -m pip install --upgrade build
	@python -m build

.PHONY: publish
publish: ## Publish to PyPI.
	@echo "Publishing to PyPI..."
	@python -m pip install --upgrade twine
	@python -m twine check dist/*
	@python -m twine upload --repository llm-guard dist/*

.PHONY: docs-serve
docs-serve: ## Serve documentation using mkdocs.
	@echo "Serving documentation..."
	@mkdocs serve -a localhost:8085

.PHONY: clean
clean: ## Clean and Remove build files and pytest cache.
	@echo "Cleaning up..."
	@rm -rf build dist .pytest_cache .egg-info llm_guard.egg-info

.PHONY: help
help: ## List all targets and help information.
	@echo "Available commands:"
	@grep --no-filename -E '^([a-z.A-Z_%-/]+:.*?)##' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?(## ?)"}; { \
			if (length($$1) > 0) { \
				printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2; \
			} else { \
				printf "%s\n", $$2; \
			} \
		}'
