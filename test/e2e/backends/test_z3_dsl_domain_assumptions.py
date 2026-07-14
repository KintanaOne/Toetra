from __future__ import annotations

from dsl.backends.defaults import create_default_backend_registry
from dsl.backends.router import BackendRouter
from dsl.backends.z3_backend.runner import VerificationStatus, Z3Runner
from dsl.ir.ir2.context import IR2BuildContext
from dsl.ir.ir2.enums import NormalFormKind
from dsl.ir.ir2.run_ir2 import run_ir2
from dsl.language.vocabulary.backends import EnumBackend


def _run(source: str):
    (task,) = run_ir2(
        source,
        context=IR2BuildContext(preferred_normal_form=NormalFormKind.NNF),
    )
    route = BackendRouter(create_default_backend_registry()).route(task)
    result = Z3Runner().run(task)
    return task, route, result


def test_z3_proves_universal_property_from_dsl_interval_domain() -> None:
    task, route, result = _run("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 with domain(x0.a: [0, 3]) => x0.a <= 3 using Z3
        """)

    assert task.backend is EnumBackend.Z3
    assert route.backend is EnumBackend.Z3
    assert len(task.assumptions) == 2
    assert task.metadata["domain_assumption_count"] == 2
    assert result.status is VerificationStatus.PROVED
    assert result.solver_status == "unsat"


def test_z3_finds_counterexample_inside_dsl_interval_domain() -> None:
    task, _, result = _run("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 with domain(x0.a: [0, 3]) => x0.a <= 2 using Z3
        """)

    assert len(task.assumptions) == 2
    assert result.status is VerificationStatus.COUNTEREXAMPLE
    assert result.solver_status == "sat"
    assert result.model is not None
    assert "x0.a" in result.model


def test_z3_returns_existential_witness_from_dsl_domain() -> None:
    task, _, result = _run("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        exists x0 with domain(x0.a: ]0, 3]) => x0.a > 2 using Z3
        """)

    assert len(task.assumptions) == 2
    assert result.status is VerificationStatus.WITNESS
    assert result.solver_status == "sat"


def test_z3_proves_property_from_numeric_finite_set_domain() -> None:
    task, _, result = _run("""
        model := "model.onnx"
        target := MyTarget

        [LOGIC]:
        forall x0 with domain(x0.a: {1, 2}) => x0.a <= 2 using Z3
        """)

    assert len(task.assumptions) == 1
    assert task.requirements.requires_finite_set_membership is True
    assert result.status is VerificationStatus.PROVED
    assert result.solver_status == "unsat"
