from __future__ import annotations

from demo.internals.affine_model_assumption_z3 import (
    BOUND_SAMPLE,
    constant_output_assumption,
    linear_output_assumption,
    run_toetra_z3_with_assumption,
)
from toetra._backends.z3_backend.runner import VerificationStatus
from toetra._language.vocabulary.backends import EnumBackend


def test_z3_e2e_proves_bound_with_constant_affine_model_assumption() -> None:
    results = run_toetra_z3_with_assumption(
        BOUND_SAMPLE,
        constant_output_assumption(),
    )

    assert len(results) == 1

    task, route, result = results[0]

    assert task.backend == EnumBackend.Z3
    assert route.backend == EnumBackend.Z3
    assert len(task.assumptions) == 1
    assert result.status == VerificationStatus.PROVED
    assert result.solver_status == "unsat"
    assert result.model is None


def test_z3_e2e_finds_counterexample_for_unbounded_linear_model_assumption() -> None:
    results = run_toetra_z3_with_assumption(
        BOUND_SAMPLE,
        linear_output_assumption(),
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
