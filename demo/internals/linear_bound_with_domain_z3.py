from __future__ import annotations

from textwrap import dedent

from toetra._backends.defaults import create_default_backend_registry
from toetra._backends.router import BackendRouter
from toetra._backends.z3_backend.runner import VerificationStatus, Z3Runner
from toetra._compiler.ir.ir1.run_ir1 import run_ir
from toetra._compiler.ir.ir2.builder import IR2Builder
from toetra._compiler.ir.ir2.context import IR2BuildContext
from toetra._compiler.ir.ir2.domain_assumptions import (
    DomainAssumptionEncoder,
    NumericFeatureBounds,
)
from toetra._compiler.ir.ir2.enums import NormalFormKind
from toetra._compiler.ir.ir2.dsl.nodes import NNFFormulaIR2
from toetra._compiler.ir.ir2.points import PointAwareIR2Analyzer
from toetra._compiler.ir.normalization.nnf import NNFNormalizer
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.encoder.factory import ModelEncoderFactory
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema

BOUND_SAMPLE = dedent("""
    model := "demo-linear.pkl"
    target := MyTarget

    [BOUND]:
    forall x0 with domain(
    
    )=> target <= 7 using Z3
    """).strip()


def linear_schema() -> ModelSchema:
    """
    Synthetic sklearn LinearRegression schema:

        _model.MyTarget == 2*x0.a + 1
    """

    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={
            "a": FeatureSchema(
                name="a",
                dtype=EnumDataType.FLOAT,
                nullable=False,
            ),
        },
        target="MyTarget",
        task="regression",
        metadata={
            "linear": {
                "coef": [2.0],
                "intercept": 1.0,
                "feature_names": ["a"],
            },
        },
    )


def proving_domain_bounds() -> tuple[NumericFeatureBounds, ...]:
    """
    Domain:

        0 <= x0.a <= 3

    Therefore:

        2*x0.a + 1 <= 7
    """

    return (
        NumericFeatureBounds(
            entity="x0",
            feature="a",
            lower=0.0,
            upper=3.0,
        ),
    )


def weak_domain_bounds() -> tuple[NumericFeatureBounds, ...]:
    """
    Domain:

        0 <= x0.a <= 4

    The property target <= 7 is no longer guaranteed, because x0.a = 7/2
    gives target = 8.
    """

    return (
        NumericFeatureBounds(
            entity="x0",
            feature="a",
            lower=0.0,
            upper=4.0,
        ),
    )


def run_toetra_z3_linear_bound_with_domains(
    source: str,
    schema: ModelSchema,
    bounds: tuple[NumericFeatureBounds, ...],
):
    """
    Toetra + ModelEncoder + DomainAssumptionEncoder + Z3 path.

    Pipeline:
        DSL source
        -> IR1
        -> NNF
        -> ModelEncoder emits MODEL assumptions
        -> DomainAssumptionEncoder emits DOMAIN assumptions
        -> IR2 builds Γ ∧ ¬P
        -> backend routing
        -> Z3 execution
    """

    ir1_tasks = run_ir(source)
    nnf_tasks = NNFNormalizer().normalize_tasks(ir1_tasks)

    if len(nnf_tasks) != 1:
        raise ValueError("This demo expects exactly one Toetra task.")

    requested_evaluations = PointAwareIR2Analyzer().model_evaluations(
        spec_formula=NNFFormulaIR2(expression=nnf_tasks[0].query.expression),
    )
    model_assumptions = ModelEncoderFactory().encode(
        schema=schema,
        evaluations=requested_evaluations,
    )

    domain_assumptions = DomainAssumptionEncoder().encode(bounds)

    assumptions = model_assumptions + domain_assumptions

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


def print_case(
    title: str,
    source: str,
    schema: ModelSchema,
    bounds: tuple[NumericFeatureBounds, ...],
    expected: VerificationStatus,
) -> None:
    print("=" * 80)
    print(title)
    print("=" * 80)
    print(source)
    print()
    print(f"Model framework   : {schema.framework.value}")
    print(f"Model type        : {schema.model_type}")
    print(f"Target            : {schema.target}")
    print(f"Linear metadata   : {schema.metadata.get('linear')}")
    print("Domain bounds     :")

    for bound in bounds:
        print(
            f"  - {bound.entity}.{bound.feature}: "
            f"lower={bound.lower}, upper={bound.upper}"
        )

    print()

    results = run_toetra_z3_linear_bound_with_domains(
        source=source,
        schema=schema,
        bounds=bounds,
    )

    for index, task_route_result in enumerate(results):
        task, route, result = task_route_result

        print(f"Task              : {index}")
        print(f"Backend routed to : {route.backend.value}")
        print(f"Route reason      : {route.reason}")
        print(f"Assumptions       : {len(task.assumptions)}")
        print(f"Requires model    : {task.requirements.requires_model_assertions}")
        print(f"Requires domains  : {task.requirements.requires_domains}")
        print(f"Normal form       : {task.normal_form.value}")
        print(f"Solver status     : {result.solver_status}")
        print(f"Toetra status      : {result.status.value}")

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
    schema = linear_schema()

    print_case(
        title="CASE 1 — Linear model bound is proved under tight input domain",
        source=BOUND_SAMPLE,
        schema=schema,
        bounds=proving_domain_bounds(),
        expected=VerificationStatus.PROVED,
    )

    print_case(
        title="CASE 2 — Linear model bound fails under weak input domain",
        source=BOUND_SAMPLE,
        schema=schema,
        bounds=weak_domain_bounds(),
        expected=VerificationStatus.COUNTEREXAMPLE,
    )

    print("✅ Linear model BOUND + domain assumptions Z3 demo succeeded.")


if __name__ == "__main__":
    main()
