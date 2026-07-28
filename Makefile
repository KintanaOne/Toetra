# =========================
# Toetra - developer commands
# =========================

.PHONY: install test test-wip test-all lint format format-check type \
	notebooks-clean notebooks-check generated-check identity-check public-contract-check snippets-check docs-check ci \
	dist dist-check install-check release-check review-bundle \
	review-bundle-check repository-check demo-regression demo-quickstart \
	demo-classification demo-check clean ci-local

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
	python scripts/ci/clean_notebooks.py demo

notebooks-check:
	python scripts/ci/clean_notebooks.py --check demo

generated-check:
	python scripts/docs/generate_numeric_compatibility_matrices.py --check

identity-check:
	python scripts/repository/check_identity_contract.py

public-contract-check:
	python scripts/ci/check_public_contract.py

repository-check:
	python scripts/repository/check_repository_contract.py

format: notebooks-clean
	python -m black .

format-check: notebooks-check
	python -m black --check .


type:
	python -m pyright

snippets-check:
	python scripts/docs/check_snippets.py

docs-check: snippets-check
	python -m mkdocs build --strict

# Non-mutating authoritative verification gate.
ci: lint format-check generated-check identity-check public-contract-check repository-check type test docs-check

# Complete local gate without Ruff for hosts that block unsigned native tools.
# Hosted CI remains authoritative for lint.
ci-local: format format-check generated-check identity-check public-contract-check repository-check type test docs-check
	
ci-local-fix: format ci-local

ci-check:
	python -m ruff check --fix
	python -m ruff check .
	python -m black .
	python -m black --check .
	python scripts/repository/check_identity_contract.py
	python -m pyright
	python -m pytest -q

# Build deterministic wheel and sdist artifacts.
dist:
	python scripts/release/build_distribution.py --output dist --check-reproducible --require-clean

dist-check:
	python scripts/release/check_distribution.py dist

# Install the wheel in a fresh venv and import Toetra outside the checkout.
install-check:
	python scripts/release/check_installed_distribution.py dist

release-check: identity-check public-contract-check repository-check dist dist-check install-check

review-bundle:
	python scripts/release/build_review_bundle.py --output dist/toetra_review_bundle.zip

review-bundle-check: identity-check repository-check
	python scripts/release/build_review_bundle.py --check-reproducible

# Run the public affine-regression demonstration.
demo-regression:
	python -m demo.regression.affine_regression

# Run the self-contained public verify(...) quickstart.
demo-quickstart:
	python -m demo.quickstart.verify_model --demo

# Run the public binary-classification release demo.
demo-classification:
	python -m demo.classification.binary_classification_policy

demo-check: demo-quickstart demo-regression demo-classification

clean:
	python -c "import shutil; [shutil.rmtree(p, ignore_errors=True) for p in ('build', 'dist', 'site')]"
	python -c "from pathlib import Path; [p.unlink() for p in Path('.').rglob('*.pyc')]"
	python -c "import shutil; from pathlib import Path; [shutil.rmtree(p, ignore_errors=True) for p in Path('.').rglob('__pycache__')]"
