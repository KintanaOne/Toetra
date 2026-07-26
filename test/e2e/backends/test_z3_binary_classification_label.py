from __future__ import annotations

from toetra._backends.defaults import create_default_backend_registry
from toetra._backends.router import BackendRouter
from toetra._backends.results import VerificationStatus
from toetra._backends.z3_backend.runner import Z3Runner
from toetra._compiler.ir.ir2.run_ir2 import run_ir2_with_model_schema
from toetra._language.vocabulary.backends import EnumBackend
from test.fixtures.binary_classification import (
    binary_label_property,
    make_sklearn_logistic_schema,
)


def _run(*, quantifier: str, label: str, decision_value: float):
    task = run_ir2_with_model_schema(
        binary_label_property(quantifier=quantifier, label=label),
        schema=make_sklearn_logistic_schema(intercept=decision_value),
    )[0]
    route = BackendRouter(create_default_backend_registry()).route(task)
    result = Z3Runner().run(task)
    return task, route, result


def test_z3_proves_positive_label_for_strictly_positive_decision_value() -> None:
    task, route, result = _run(
        quantifier="forall",
        label="approved",
        decision_value=1.0,
    )
    assert task.backend is EnumBackend.Z3
    assert route.backend is EnumBackend.Z3
    assert result.status is VerificationStatus.PROVED
    assert result.solver_status == "unsat"
    assert result.model is None


def test_z3_finds_counterexample_for_positive_label_at_zero_boundary() -> None:
    _task, _route, result = _run(
        quantifier="forall",
        label="approved",
        decision_value=0.0,
    )
    assert result.status is VerificationStatus.COUNTEREXAMPLE
    assert result.solver_status == "sat"
    assert result.model is not None
    quantity_names = tuple(
        name for name in result.model if "oriented_decision_value" in name
    )
    assert len(quantity_names) == 1
    assert str(result.model[quantity_names[0]]) == "0"


def test_z3_proves_negative_label_at_zero_boundary() -> None:
    _task, _route, result = _run(
        quantifier="forall",
        label="rejected",
        decision_value=0.0,
    )
    assert result.status is VerificationStatus.PROVED
    assert result.solver_status == "unsat"


def test_z3_returns_witness_for_satisfiable_positive_label() -> None:
    _task, _route, result = _run(
        quantifier="exists",
        label="approved",
        decision_value=1.0,
    )
    assert result.status is VerificationStatus.WITNESS
    assert result.solver_status == "sat"
    assert result.model is not None


def test_z3_returns_no_witness_for_unsatisfiable_positive_label() -> None:
    _task, _route, result = _run(
        quantifier="exists",
        label="approved",
        decision_value=-1.0,
    )
    assert result.status is VerificationStatus.NO_WITNESS
    assert result.solver_status == "unsat"
