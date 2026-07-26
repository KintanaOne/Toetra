from __future__ import annotations

from toetra._backends.defaults import create_default_backend_registry
from toetra._backends.router import BackendRouter
from toetra._backends.z3_backend.runner import VerificationStatus, Z3Runner
from toetra._compiler.ir.ir1.nodes import (
    ComparisonIR,
    ConstantExpressionIR,
    TargetExpressionIR,
)
from toetra._compiler.ir.ir2.context import IR2BuildContext
from toetra._compiler.ir.ir2.enums import NormalFormKind
from toetra._compiler.ir.ir2.run_ir2 import run_ir2_with_model_schema
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema


def _schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={"a": FeatureSchema(name="a", dtype=EnumDataType.FLOAT)},
        target="score",
        target_dtype=EnumDataType.FLOAT,
        task="regression",
        metadata={
            "linear": {
                "coef": [2.0],
                "intercept": 1.0,
                "feature_names": ["a"],
            }
        },
    )


def test_same_global_constant_is_reused_across_properties() -> None:
    source = """
        model := "linear.joblib"
        target := score

        max_score := 7.0
        minimum_a := 0.0
        maximum_a := 3.0

        [BOUND]:
        forall x0
            with domain(x0.a: [minimum_a, maximum_a])
            => target <= max_score
            using Z3

        [LOGIC]:
        forall x0
            with domain(x0.a: [minimum_a, maximum_a])
            => target < max_score
            using Z3
    """
    tasks = run_ir2_with_model_schema(
        source,
        schema=_schema(),
        ir2_context=IR2BuildContext(preferred_normal_form=NormalFormKind.NNF),
    )

    assert len(tasks) == 2
    router = BackendRouter(create_default_backend_registry())
    runner = Z3Runner()
    results = []
    thresholds = []

    for task in tasks:
        router.route(task)
        results.append(runner.run(task))
        comparison = task.spec_formula.expression
        assert isinstance(comparison, ComparisonIR)
        assert isinstance(comparison.left, TargetExpressionIR)
        assert comparison.left.dtype is EnumDataType.FLOAT
        assert isinstance(comparison.right, ConstantExpressionIR)
        thresholds.append(comparison.right)

    assert [result.status for result in results] == [
        VerificationStatus.PROVED,
        VerificationStatus.COUNTEREXAMPLE,
    ]
    assert [threshold.value for threshold in thresholds] == [7.0, 7.0]
    assert [threshold.source_name for threshold in thresholds] == [
        "max_score",
        "max_score",
    ]
    assert all("max_score" not in (result.model or {}) for result in results)


def test_model_schema_dtypes_reach_user_scalar_ir_before_backend_translation() -> None:
    source = """
        model := "linear.joblib"
        target := score

        [LOGIC]:
        forall x0 => target - 2.0 * x0.a == 1.0 using Z3
    """
    (task,) = run_ir2_with_model_schema(
        source,
        schema=_schema(),
        ir2_context=IR2BuildContext(preferred_normal_form=NormalFormKind.NNF),
    )

    comparison = task.spec_formula.expression
    assert isinstance(comparison, ComparisonIR)
    assert comparison.left.dtype is EnumDataType.FLOAT
