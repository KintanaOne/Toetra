# =========================
# FORML - Makefile minimal
# =========================

.PHONY: install test test-wip test-all lint format format-check type ci clean

# Install dev environment
install:
	pip install -r requirements-dev.txt

# Run stable tests only
test:
	pytest -q -m "not wip"

# Run only WIP tests
test-wip:
	pytest -q -m "wip"

# Run all tests
test-all:
	pytest -q

# Run linting
lint:
	ruff check .

# Format code
format:
	black .

# Verify formatting
format-check:
	black --check .

# Type checking
type:
	pyright dsl/

# Full local CI
ci:
	ruff check .
	black --check .
	pytest -q -m "not wip"
	pyright dsl/

# Clean caches
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete