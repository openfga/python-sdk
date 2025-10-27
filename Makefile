.PHONY: sync test lint fmt fix check doc

# Install/update dependencies
sync:
	uv sync

# Run tests with coverage
# Usage: make test
# To run a specific test: make test TEST=test_file.py::test_function
test:
	uv run pytest --cov-report term-missing --cov=openfga_sdk $(if $(TEST),$(TEST),test/)

# Run linter
lint:
	uv run ruff check .

# Format code
fmt:
	uv run ruff format .

# Fix fixable linting and formatting issues
fix:
	uv run ruff check --fix .
	uv run ruff format .

# Run checks (lint + test)
check: lint fmt test

# Show help
doc:
	@echo "Available targets:"
	@echo "  sync    - Install/update dependencies"
	@echo "  test    - Run tests with coverage (use TEST=path.to.test to run specific tests)"
	@echo "  lint    - Run linter checks"
	@echo "  fmt     - Format code"
	@echo "  fix     - Fix fixable linting and formatting issues"
	@echo "  check   - Run both linting and tests"
	@echo "  doc     - Show this help message"
