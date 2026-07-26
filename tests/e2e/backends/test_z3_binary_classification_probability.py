from __future__ import annotations

from toetra._backends.results import VerificationStatus
from toetra._backends.z3_backend.runner import Z3Runner
from toetra._compiler.ir.ir2.run_ir2 import run_ir2_with_model_schema
from tests.support.binary_classification import (
    binary_probability_property,
    make_sklearn_logistic_schema,
)


def _run(
    *,
    quantifier: str = "forall",
    label: str = "approved",
    operator: str = ">=",
    threshold: str = "0.8",
    decision_value: float,
):
    task = run_ir2_with_model_schema(
        binary_probability_property(
            quantifier=quantifier,
            label=label,
            operator=operator,
            threshold=threshold,
        ),
        schema=make_sklearn_logistic_schema(intercept=decision_value),
    )[0]
    return task, Z3Runner().run(task)


def test_z3_proves_positive_probability_above_non_exact_threshold() -> None:
    task, result = _run(decision_value=2.0)

    assert result.status is VerificationStatus.PROVED
    evidence = task.lowering_evidence[0]
    assert evidence.canonical_constraint.threshold.startswith("1.386294")
    assert evidence.canonical_constraint.selected_bound == "upper"


def test_z3_returns_witness_for_positive_probability() -> None:
    _task, result = _run(quantifier="exists", decision_value=2.0)

    assert result.status is VerificationStatus.WITNESS


def test_half_probability_threshold_is_exact_at_zero() -> None:
    task, result = _run(threshold="0.5", decision_value=0.0)

    assert result.status is VerificationStatus.PROVED
    assert task.lowering_evidence[0].canonical_constraint.threshold == "0"


def test_negative_label_probability_uses_reversed_decision_orientation() -> None:
    _task, result = _run(label="rejected", decision_value=-2.0)

    assert result.status is VerificationStatus.PROVED
