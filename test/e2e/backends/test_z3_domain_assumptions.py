from __future__ import annotations

from textwrap import dedent

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
from dsl.ir.ir2.enums import NormalFormKind
from dsl.ir.normalization.nnf import NNFNormalizer
from dsl.language.vocabulary.backends import EnumBackend

DOMAIN_PROVED_SAMPLE = """
model := "model.onnx"
target := MyTarget

[BOUND]:
forall x0
    => x0.a <= 3.0
    using Z3
"""


DOMAIN_COUNTEREXAMPLE_SAMPLE = dedent("""
    model := "demo.onnx"
    target := MyTarget

    [LOGIC]:
    forall x0 => x0.a <= 2 using Z3
    """).strip()


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


def test_z3_e2e_proves_property_from_numeric_domain_bound() -> None:
    results = _run_with_domain_bounds(
        DOMAIN_PROVED_SAMPLE,
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

    assert task.backend == EnumBackend.Z3
    assert route.backend == EnumBackend.Z3
    assert len(task.assumptions) == 2
    assert task.requirements.requires_domains is True

    assert result.status == VerificationStatus.PROVED
    assert result.solver_status == "unsat"
    assert result.model is None


def test_z3_e2e_finds_counterexample_when_domain_bound_is_too_weak() -> None:
    results = _run_with_domain_bounds(
        DOMAIN_COUNTEREXAMPLE_SAMPLE,
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

    assert task.backend == EnumBackend.Z3
    assert route.backend == EnumBackend.Z3
    assert len(task.assumptions) == 2
    assert task.requirements.requires_domains is True

    assert result.status == VerificationStatus.COUNTEREXAMPLE
    assert result.solver_status == "sat"
    assert result.model is not None
    assert "x0.a" in result.model
