from __future__ import annotations

from dataclasses import replace
from textwrap import dedent

from dsl.backends.defaults import create_default_backend_registry
from dsl.backends.router import BackendRouter
from dsl.backends.z3_backend.runner import VerificationStatus, Z3Runner
from dsl.ir.ir1.nodes import ModelEvaluationIR
from dsl.ir.ir1.run_ir1 import run_ir
from dsl.ir.ir2.builder import IR2Builder
from dsl.ir.ir2.context import IR2BuildContext
from dsl.ir.ir2.enums import AssumptionSource, NormalFormKind
from dsl.ir.ir2.nodes import (
    AffineExpressionIR2,
    AffineOutputConstraintIR2,
    AffineTermIR2,
    AssumptionIR2,
    NNFFormulaIR2,
)
from dsl.ir.normalization.nnf import NNFNormalizer
from dsl.language.vocabulary.operators import EnumComparisonOperator

BOUND_SAMPLE = dedent("""
    model := "demo-linear.onnx"
    target := MyTarget

    [BOUND]:
    forall x0 => target <= 7 using Z3
    """).strip()


def constant_output_assumption() -> AssumptionIR2:
    """
    Manual model assumption:

        _model.MyTarget == 3

    Under this assumption, the property:

        target <= 7

    must be proved.
    """

    atom = AffineOutputConstraintIR2(
        output_entity="_model",
        output_feature="MyTarget",
        op=EnumComparisonOperator.EQ,
        expression=AffineExpressionIR2(
            terms=(),
            bias=3.0,
        ),
        metadata={
            "demo": "constant affine output",
        },
    )

    return AssumptionIR2(
        source=AssumptionSource.MODEL,
        formula=NNFFormulaIR2(expression=atom),
        description="manual constant affine model output",
        metadata={
            "equation": "_model.MyTarget == 3",
        },
    )


def linear_output_assumption() -> AssumptionIR2:
    """
    Manual model assumption:

        _model.MyTarget == 2*x0.a + 1

    Without an input domain on x0.a, the property:

        target <= 7

    is not guaranteed. Z3 should find a counterexample.
    """

    atom = AffineOutputConstraintIR2(
        output_entity="_model",
        output_feature="MyTarget",
        op=EnumComparisonOperator.EQ,
        expression=AffineExpressionIR2(
            terms=(
                AffineTermIR2(
                    entity="x0",
                    feature="a",
                    coefficient=2.0,
                ),
            ),
            bias=1.0,
        ),
        metadata={
            "demo": "linear affine output",
        },
    )

    return AssumptionIR2(
        source=AssumptionSource.MODEL,
        formula=NNFFormulaIR2(expression=atom),
        description="manual linear affine model output",
        metadata={
            "equation": "_model.MyTarget == 2*x0.a + 1",
        },
    )


def run_forml_z3_with_assumption(
    source: str,
    assumption: AssumptionIR2,
):
    """
    Minimal FORML + manual model assumption + Z3 path.

    Pipeline:
        DSL source
        -> IR1
        -> NNF
        -> IR2 with manual MODEL assumption
        -> backend routing
        -> Z3 execution
    """

    ir1_tasks = run_ir(source)
    nnf_tasks = NNFNormalizer().normalize_tasks(ir1_tasks)

    builder = IR2Builder()
    ir2_tasks = []
    for task in nnf_tasks:
        spec_formula = NNFFormulaIR2(expression=task.query.expression)
        evaluations = builder.point_analyzer.model_evaluations(
            spec_formula=spec_formula,
        )
        if len(evaluations) != 1:
            raise ValueError(
                "Manual affine demo assumptions require exactly one model evaluation."
            )
        bound_assumption = _bind_manual_assumption(assumption, evaluations[0])
        ir2_tasks.append(
            builder.build(
                task,
                assumptions=(bound_assumption,),
                context=IR2BuildContext(
                    preferred_normal_form=NormalFormKind.NNF,
                    backend_hint=None,
                ),
            )
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


def _bind_manual_assumption(
    assumption: AssumptionIR2,
    evaluation: ModelEvaluationIR,
) -> AssumptionIR2:
    """Migrate one legacy demo equation to an explicit evaluation identity."""

    atom = assumption.formula.expression
    if not isinstance(atom, AffineOutputConstraintIR2):
        raise TypeError("Manual affine demo assumption must wrap an affine equation.")
    point = evaluation.point
    expression = replace(
        atom.expression,
        terms=tuple(
            replace(term, entity=point.name, point=point)
            for term in atom.expression.terms
        ),
    )
    return replace(
        assumption,
        formula=NNFFormulaIR2(
            expression=replace(
                atom,
                expression=expression,
                evaluation=evaluation,
            )
        ),
    )


def print_case(
    title: str,
    source: str,
    assumption: AssumptionIR2,
    expected: VerificationStatus,
) -> None:
    print("=" * 80)
    print(title)
    print("=" * 80)
    print(source)
    print()
    print(f"Assumption        : {assumption.description}")
    print(f"Equation          : {assumption.metadata.get('equation')}")
    print()

    results = run_forml_z3_with_assumption(source, assumption)

    for index, task_route_result in enumerate(results):
        task, route, result = task_route_result

        print(f"Task              : {index}")
        print(f"Backend routed to : {route.backend.value}")
        print(f"Route reason      : {route.reason}")
        print(f"Normal form       : {task.normal_form.value}")
        print(f"Solver status     : {result.solver_status}")
        print(f"FORML status      : {result.status.value}")

        if result.model:
            print("Counterexample    :")
            for name, value in result.model.items():
                print(f"  - {name} = {value}")

        print()

        if result.status != expected:
            raise AssertionError(
                f"Expected {expected.value}, got {result.status.value}"
            )


def main() -> None:
    print_case(
        title="CASE 1 — Constant affine model output proves target bound",
        source=BOUND_SAMPLE,
        assumption=constant_output_assumption(),
        expected=VerificationStatus.PROVED,
    )

    print_case(
        title="CASE 2 — Linear affine model output needs input domains",
        source=BOUND_SAMPLE,
        assumption=linear_output_assumption(),
        expected=VerificationStatus.COUNTEREXAMPLE,
    )

    print("✅ Manual affine model assumption Z3 demo succeeded.")


if __name__ == "__main__":
    main()
