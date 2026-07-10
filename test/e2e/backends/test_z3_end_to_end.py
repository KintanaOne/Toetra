from __future__ import annotations

from demo.end_to_end_z3 import (
    COUNTEREXAMPLE_SAMPLE,
    PROVED_SAMPLE,
    run_forml_z3,
)
from dsl.backends.z3_backend.runner import VerificationStatus
from dsl.language.vocabulary.backends import EnumBackend


def test_z3_end_to_end_proves_tautological_property() -> None:
    results = run_forml_z3(PROVED_SAMPLE)

    assert len(results) == 1

    task, route, result = results[0]

    assert task.backend == EnumBackend.Z3
    assert route.backend == EnumBackend.Z3
    assert result.status == VerificationStatus.PROVED
    assert result.solver_status == "unsat"
    assert result.model is None


def test_z3_end_to_end_returns_counterexample_for_violated_property() -> None:
    results = run_forml_z3(COUNTEREXAMPLE_SAMPLE)

    assert len(results) == 1

    task, route, result = results[0]

    assert task.backend == EnumBackend.Z3
    assert route.backend == EnumBackend.Z3
    assert result.status == VerificationStatus.COUNTEREXAMPLE
    assert result.solver_status == "sat"
    assert result.model is not None
    assert "x0.a" in result.model
