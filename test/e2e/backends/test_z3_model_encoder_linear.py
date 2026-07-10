from __future__ import annotations

from demo.model_encoder_linear_z3 import (
    BOUND_SAMPLE,
    constant_like_linear_schema,
    run_forml_z3_with_model_encoder,
    unbounded_linear_schema,
)
from dsl.backends.z3_backend.runner import VerificationStatus
from dsl.language.vocabulary.backends import EnumBackend


def test_z3_e2e_proves_bound_with_model_encoder_constant_like_linear_model() -> None:
    results = run_forml_z3_with_model_encoder(
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


def test_z3_e2e_finds_counterexample_with_model_encoder_unbounded_linear_model() -> (
    None
):
    results = run_forml_z3_with_model_encoder(
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
