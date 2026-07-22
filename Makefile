# =========================
# FORML - developer commands
# =========================

.PHONY: install test test-wip test-all lint format format-check type \
	notebooks-clean notebooks-check generated-check public-contract-check docs-check ci \
	release-metadata dist dist-check install-check release-check review-bundle \
	review-bundle-check demo-affine demo-user demo-classification clean

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
	python scripts/clean_notebooks.py demo/notebooks

notebooks-check:
	python scripts/clean_notebooks.py --check demo/notebooks

generated-check:
	python scripts/generate_numeric_compatibility_matrices.py --check

public-contract-check:
	python scripts/check_public_contract.py

format: notebooks-clean
	python -m black .

format-check: notebooks-check
	python -m black --check .

type:
	python -m pyright

docs-check:
	python -m mkdocs build --strict

# Non-mutating local verification gate.
ci: lint format-check generated-check public-contract-check type test docs-check

ci-check:
	python -m ruff check --fix
	python -m ruff check .
	python -m black .
	python -m black --check .
	python -m pyright
	python -m pytest -q

release-metadata:
	python scripts/prepare_rc2_changelog.py

# Build deterministic wheel and sdist artifacts.
dist:
	python scripts/build_distribution.py --output dist --check-reproducible

dist-check:
	python scripts/check_distribution.py dist

# Install the wheel in a fresh venv and import FORML outside the checkout.
install-check:
	python scripts/check_installed_distribution.py dist

release-check: dist dist-check install-check

review-bundle:
	python scripts/build_review_bundle.py --output dist/forml_review_bundle.zip

review-bundle-check:
	python scripts/build_review_bundle.py --check-reproducible

# Run the canonical affine end-to-end demo.
demo-affine:
	python -m demo.affine_specification_constants_z3

# Run the self-contained public verify(...) script example.
demo-user:
	python -m demo.user_verify_script --demo

# Run the public binary-classification release demo.
demo-classification:
	python -m demo.binary_classification_policy

clean:
	python -c "import shutil; [shutil.rmtree(p, ignore_errors=True) for p in ('build', 'dist', 'site')]"
	python -c "from pathlib import Path; [p.unlink() for p in Path('.').rglob('*.pyc')]"
	python -c "import shutil; from pathlib import Path; [shutil.rmtree(p, ignore_errors=True) for p in Path('.').rglob('__pycache__')]"
