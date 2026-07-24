from __future__ import annotations

from demo.internals.linear_regression_encoder_z3 import (
    BOUND_SAMPLE,
    constant_like_linear_schema,
    run_linear_regression_encoder,
    unbounded_linear_schema,
)
from dsl.backends.z3_backend.runner import VerificationStatus
from dsl.language.vocabulary.backends import EnumBackend


def test_z3_linear_regression_encoder_proves_constant_like_model() -> None:
    results = run_linear_regression_encoder(
        BOUND_SAMPLE,
        constant_like_linear_schema(),
    )

    assert len(results) == 1

    task, route, result = results[0]

    assert task.backend == EnumBackend.Z3
    assert route.backend == EnumBackend.Z3
    assert len(task.assumptions) == 1
    assert result.status == VerificationStatus.PROVED
    assert result.solver_status == "unsat"
    assert result.model is None


def test_z3_linear_regression_encoder_finds_unbounded_counterexample() -> None:
    results = run_linear_regression_encoder(
        BOUND_SAMPLE,
        unbounded_linear_schema(),
    )

    assert len(results) == 1

    task, route, result = results[0]

    assert task.backend == EnumBackend.Z3
    assert route.backend == EnumBackend.Z3
    assert len(task.assumptions) == 1
    assert result.status == VerificationStatus.COUNTEREXAMPLE
    assert result.solver_status == "sat"
    assert result.model is not None
    assert "_model.MyTarget" in result.model
    assert "x0.a" in result.model
