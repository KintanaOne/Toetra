from __future__ import annotations

from dsl.backends.defaults import create_default_backend_registry
from dsl.backends.router import BackendRouter
from dsl.backends.z3_backend.runner import VerificationStatus, Z3Runner
from dsl.ir.ir1.run_ir1 import run_ir
from dsl.ir.ir2.builder import IR2Builder
from dsl.ir.ir2.context import IR2BuildContext
from dsl.ir.ir2.domain_assumptions import (
    DomainAssumptionEncoder,
    NumericFeatureBounds,
)
from dsl.ir.ir2.enums import (
    NormalFormKind,
    VerificationSemantics,
)
from dsl.ir.normalization.nnf import NNFNormalizer
from dsl.language.vocabulary.backends import EnumBackend

EXISTENTIAL_WITNESS_SAMPLE = """
model := "demo.onnx"
target := MyTarget

[LOGIC]:
exists x0
    => x0.a > 2.0
    using Z3
"""


EXISTENTIAL_NO_WITNESS_SAMPLE = """
model := "demo.onnx"
target := MyTarget

[LOGIC]:
exists x0
    => x0.a > 10.0
    using Z3
"""


def _run_with_domain_bounds(
    source: str,
    bounds: tuple[NumericFeatureBounds, ...],
):
    ir1_tasks = run_ir(source)
    nnf_tasks = NNFNormalizer().normalize_tasks(ir1_tasks)

    assumptions = DomainAssumptionEncoder().encode(bounds)

    ir2_tasks = IR2Builder().build_tasks(
        nnf_tasks,
        assumptions=assumptions,
        context=IR2BuildContext(
            preferred_normal_form=NormalFormKind.NNF,
            backend_hint=None,
        ),
    )

    registry = create_default_backend_registry()
    router = BackendRouter(registry)
    runner = Z3Runner()

    results = []

    for task in ir2_tasks:
        route = router.route(task)
        result = runner.run(task)
        results.append((task, route, result))

    return results


def test_z3_e2e_returns_witness_for_satisfiable_existential_property() -> None:
    results = _run_with_domain_bounds(
        EXISTENTIAL_WITNESS_SAMPLE,
        (
            NumericFeatureBounds(
                entity="x0",
                feature="a",
                lower=0.0,
                upper=3.0,
            ),
        ),
    )

    assert len(results) == 1

    task, route, result = results[0]

    assert task.backend is EnumBackend.Z3
    assert route.backend is EnumBackend.Z3

    assert task.scope.kind == "quantifier"
    assert task.scope.quantifier == "exists"

    assert task.semantics is VerificationSemantics.SATISFACTION
    assert (
        task.requirements.required_verification_semantics
        is VerificationSemantics.SATISFACTION
    )

    assert task.requirements.uses_quantified_scope is True
    assert task.requirements.requires_native_quantifiers is False
    assert task.requirements.requires_domains is True

    # NumericFeatureBounds emits one lower-bound assumption and one
    # upper-bound assumption.
    assert len(task.assumptions) == 2

    assert result.status is VerificationStatus.WITNESS
    assert result.solver_status == "sat"
    assert result.model is not None
    assert "x0.a" in result.model


def test_z3_e2e_returns_no_witness_for_unsatisfiable_existential_property() -> None:
    results = _run_with_domain_bounds(
        EXISTENTIAL_NO_WITNESS_SAMPLE,
        (
            NumericFeatureBounds(
                entity="x0",
                feature="a",
                lower=0.0,
                upper=3.0,
            ),
        ),
    )

    assert len(results) == 1

    task, route, result = results[0]

    assert task.backend is EnumBackend.Z3
    assert route.backend is EnumBackend.Z3

    assert task.scope.kind == "quantifier"
    assert task.scope.quantifier == "exists"

    assert task.semantics is VerificationSemantics.SATISFACTION
    assert (
        task.requirements.required_verification_semantics
        is VerificationSemantics.SATISFACTION
    )

    assert task.requirements.uses_quantified_scope is True
    assert task.requirements.requires_native_quantifiers is False
    assert task.requirements.requires_domains is True

    assert len(task.assumptions) == 2

    assert result.status is VerificationStatus.NO_WITNESS
    assert result.solver_status == "unsat"
    assert result.model is None
