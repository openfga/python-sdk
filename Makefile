.PHONY: sync test lint fmt fix check doc update-equivalent-checks-cases

# openfga/language commit to copy the shared equivalent-checks cases from
LANGUAGE_REF ?= 5afcf707e44aa21d8ae17e47938b3f0164a13cc7

# Install/update dependencies
sync:
	uv sync

# Run tests with coverage (excludes integration tests)
# Usage: make test
# To run a specific test: make test TEST=test_file.py::test_function
test:
	uv run pytest -m "not integration" --cov-report term-missing --cov=openfga_sdk $(if $(TEST),$(TEST),test/)

test-integration:
	uv run pytest -m integration --cov-report term-missing --cov=openfga_sdk $(if $(TEST),$(TEST),test/)

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

# Copy the shared equivalent-checks cases from openfga/language
# Usage: make update-equivalent-checks-cases LANGUAGE_REF=<commit>
update-equivalent-checks-cases:
	curl -fsSL https://raw.githubusercontent.com/openfga/language/$(LANGUAGE_REF)/tests/data/equivalent-checks-cases.json -o test/data/equivalent-checks-cases.json

# Run checks (lint + test)
check: lint fmt test

# Show help
doc:
	@echo "Available targets:"
	@echo "  sync    - Install/update dependencies"
	@echo "  test    - Run tests with coverage (excludes integration tests, use TEST=path.to.test to run specific tests)"
	@echo "  test-integration - Run integration tests with coverage"
	@echo "  lint    - Run linter checks"
	@echo "  fmt     - Format code"
	@echo "  fix     - Fix fixable linting and formatting issues"
	@echo "  check   - Run both linting and tests"
	@echo "  update-equivalent-checks-cases - Copy the shared equivalent-checks cases from openfga/language (LANGUAGE_REF=<commit>)"
	@echo "  doc     - Show this help message"
