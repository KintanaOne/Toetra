# =========================
# Toetra - developer commands
# =========================

.PHONY: install test test-wip test-all lint format format-check type \
	notebooks-clean notebooks-check generated-check identity-check public-contract-check docs-check ci \
	dist dist-check install-check release-check review-bundle \
	review-bundle-check demo-regression demo-quickstart demo-classification clean \
	ci-local

install:
	python -m pip install -e ".[dev,docs]"
	
test:
	python -m pytest -q -m "not wip"

test-wip:
	python -m pytest -q -m "wip"

test-all:
	python -m pytest -q

lint:
	python -m ruff check .

notebooks-clean:
	python scripts/clean_notebooks.py demo

notebooks-check:
	python scripts/clean_notebooks.py --check demo

generated-check:
	python scripts/generate_numeric_compatibility_matrices.py --check

identity-check:
	python scripts/check_identity_contract.py

public-contract-check:
	python scripts/check_public_contract.py

format: notebooks-clean
	python -m black .

format-check: notebooks-check
	python -m black .
	python -m black --check .


type:
	python -m pyright

docs-check:
	python -m mkdocs build --strict

# Non-mutating authoritative verification gate.
ci: lint format-check generated-check identity-check public-contract-check type test docs-check

# Complete local gate without Ruff for hosts that block unsigned native tools.
# Hosted CI remains authoritative for lint.
ci-local: format-check generated-check identity-check public-contract-check type test docs-check
	
ci-check:
	python -m ruff check --fix
	python -m ruff check .
	python -m black .
	python -m black --check .
	python scripts/check_identity_contract.py
	python -m pyright
	python -m pytest -q

# Build deterministic wheel and sdist artifacts.
dist:
	python scripts/build_distribution.py --output dist --check-reproducible --require-clean

dist-check:
	python scripts/check_distribution.py dist

# Install the wheel in a fresh venv and import Toetra outside the checkout.
install-check:
	python scripts/check_installed_distribution.py dist

release-check: identity-check dist dist-check install-check

review-bundle:
	python scripts/build_review_bundle.py --output dist/toetra_review_bundle.zip

review-bundle-check: identity-check
	python scripts/build_review_bundle.py --check-reproducible

# Run the public affine-regression demonstration.
demo-regression:
	python -m demo.regression.affine_regression

# Run the self-contained public verify(...) quickstart.
demo-quickstart:
	python -m demo.quickstart.verify_model --demo

# Run the public binary-classification release demo.
demo-classification:
	python -m demo.classification.binary_classification_policy

clean:
	python -c "import shutil; [shutil.rmtree(p, ignore_errors=True) for p in ('build', 'dist', 'site')]"
	python -c "from pathlib import Path; [p.unlink() for p in Path('.').rglob('*.pyc')]"
	python -c "import shutil; from pathlib import Path; [shutil.rmtree(p, ignore_errors=True) for p in Path('.').rglob('__pycache__')]"
