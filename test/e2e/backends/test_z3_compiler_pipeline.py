from __future__ import annotations

from demo.internals.compiler_pipeline_z3 import (
    COUNTEREXAMPLE_SAMPLE,
    PROVED_SAMPLE,
    run_compiler_pipeline,
)
from dsl.backends.z3_backend.runner import VerificationStatus
from dsl.language.vocabulary.backends import EnumBackend


def test_z3_compiler_pipeline_proves_tautological_property() -> None:
    results = run_compiler_pipeline(PROVED_SAMPLE)

    assert len(results) == 1

    task, route, result = results[0]

    assert task.backend == EnumBackend.Z3
    assert route.backend == EnumBackend.Z3
    assert result.status == VerificationStatus.PROVED
    assert result.solver_status == "unsat"
    assert result.model is None


def test_z3_compiler_pipeline_returns_counterexample_for_violated_property() -> None:
    results = run_compiler_pipeline(COUNTEREXAMPLE_SAMPLE)

    assert len(results) == 1

    task, route, result = results[0]

    assert task.backend == EnumBackend.Z3
    assert route.backend == EnumBackend.Z3
    assert result.status == VerificationStatus.COUNTEREXAMPLE
    assert result.solver_status == "sat"
    assert result.model is not None
    assert "x0.a" in result.model
