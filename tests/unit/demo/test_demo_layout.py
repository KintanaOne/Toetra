from __future__ import annotations

from pathlib import Path

DEMO_ROOT = Path(__file__).parents[3] / "demo"
EXPECTED_CATEGORIES = {"classification", "internals", "quickstart", "regression"}
EXPECTED_ENTRYPOINTS = {
    "classification/binary_classification_policy.toetra",
    "classification/binary_classification_policy.ipynb",
    "classification/binary_classification_policy.py",
    "internals/affine_model_assumption_z3.py",
    "internals/compiler_pipeline_z3.py",
    "internals/linear_bound_with_domain_z3.py",
    "internals/linear_regression_encoder_z3.py",
    "quickstart/verification_policy.toetra",
    "quickstart/verify_model.py",
    "regression/affine_regression.py",
    "regression/affine_regression_policy.toetra",
    "regression/credit_risk_validation.ipynb",
}
IGNORED_LOCAL_DIRECTORIES = {"__pycache__", ".ipynb_checkpoints"}


def test_demo_root_is_grouped_by_intent() -> None:
    categories = {
        path.name
        for path in DEMO_ROOT.iterdir()
        if (
            path.is_dir()
            and path.name not in IGNORED_LOCAL_DIRECTORIES
            and any(path.iterdir())
        )
    }

    assert categories == EXPECTED_CATEGORIES
    assert not tuple(DEMO_ROOT.glob("*.py"))
    assert not tuple(DEMO_ROOT.glob("*.toetra"))

    legacy_notebook_root = DEMO_ROOT / "notebooks"
    if legacy_notebook_root.exists():
        assert not tuple(legacy_notebook_root.iterdir())


def test_demo_entrypoints_use_canonical_names() -> None:
    entrypoints = {
        path.relative_to(DEMO_ROOT).as_posix()
        for category in EXPECTED_CATEGORIES
        for path in (DEMO_ROOT / category).iterdir()
        if path.is_file()
    }

    assert entrypoints == EXPECTED_ENTRYPOINTS
