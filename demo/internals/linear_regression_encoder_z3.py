from __future__ import annotations

from textwrap import dedent

from dsl.backends.defaults import create_default_backend_registry
from dsl.backends.router import BackendRouter
from dsl.backends.z3_backend.runner import VerificationStatus, Z3Runner
from dsl.ir.ir1.run_ir1 import run_ir
from dsl.ir.ir2.builder import IR2Builder
from dsl.ir.ir2.context import IR2BuildContext
from dsl.ir.ir2.enums import NormalFormKind
from dsl.ir.ir2.nodes import NNFFormulaIR2
from dsl.ir.ir2.points import PointAwareIR2Analyzer
from dsl.ir.normalization.nnf import NNFNormalizer
from dsl.semantic.types.enums import EnumDataType
from model.detector.model_framework import EnumModelFramework
from model.encoder.factory import ModelEncoderFactory
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema

BOUND_SAMPLE = dedent("""
    model := "demo-linear.pkl"
    target := MyTarget

    [BOUND]:
    forall x0 => target <= 7 using Z3
    """).strip()


def constant_like_linear_schema() -> ModelSchema:
    """
    Synthetic sklearn LinearRegression schema:

        _model.MyTarget == 0*x0.a + 3

    Therefore:

        target <= 7

    must be proved.
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
                "coef": [0.0],
                "intercept": 3.0,
                "feature_names": ["a"],
            },
        },
    )


def unbounded_linear_schema() -> ModelSchema:
    """
    Synthetic sklearn LinearRegression schema:

        _model.MyTarget == 2*x0.a + 1

    Without input domains, the property:

        target <= 7

    is not guaranteed.
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


def run_linear_regression_encoder(
    source: str,
    schema: ModelSchema,
):
    """
    Minimal Toetra + ModelEncoder + Z3 path.

    Pipeline:
        DSL source
        -> IR1
        -> NNF
        -> ModelEncoder(schema, evaluations) produces MODEL assumptions
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
    assumptions = ModelEncoderFactory().encode(
        schema=schema,
        evaluations=requested_evaluations,
    )

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
    print()

    results = run_linear_regression_encoder(source, schema)

    for index, task_route_result in enumerate(results):
        task, route, result = task_route_result

        print(f"Task              : {index}")
        print(f"Backend routed to : {route.backend.value}")
        print(f"Route reason      : {route.reason}")
        print(f"Assumptions       : {len(task.assumptions)}")
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
    print_case(
        title="CASE 1 — ModelEncoder emits constant-like LinearRegression assumption",
        source=BOUND_SAMPLE,
        schema=constant_like_linear_schema(),
        expected=VerificationStatus.PROVED,
    )

    print_case(
        title="CASE 2 — ModelEncoder emits unbounded LinearRegression assumption",
        source=BOUND_SAMPLE,
        schema=unbounded_linear_schema(),
        expected=VerificationStatus.COUNTEREXAMPLE,
    )

    print("✅ ModelEncoder LinearRegression → IR2 → Z3 demo succeeded.")


if __name__ == "__main__":
    main()
