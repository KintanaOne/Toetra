# =========================
# FORML - Makefile minimal
# =========================

.PHONY: install test lint format type ci clean

# Install dev environment
install:
	pip install -r requirements-dev.txt

# Run all tests
test:
	pytest -q -m "not wip"

test-wip:
	pytest -q -m "wip"

test-all:
	pytest -q

# Run linting
lint:
	ruff check .

# Format code
format:
	black .

# Type checking
type:
	pyright

# Full local CI (same as GitHub Actions)
ci:
	ruff check .
	black --check .
	pytest -q
	pyright

# Clean caches
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete