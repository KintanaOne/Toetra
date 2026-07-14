# =========================
# FORML - Makefile minimal
# =========================

.PHONY: install test test-wip test-all lint format format-check type ci demo-affine demo-user clean

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
	python -m ruff check .
	python -m black .
	python -m black --check .
	python -m pyright
	python -m pytest -q

# Run the canonical affine end-to-end demo
demo-affine:
	python -m demo.affine_specification_constants_z3

# Run the self-contained public verify(...) script example
demo-user:
	python -m demo.user_verify_script --demo

# Clean caches
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete