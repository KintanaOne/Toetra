from dsl.ir.ir1.nodes import (
    AttributeExpressionIR,
    ComparisonIR,
    ConstantExpressionIR,
    QueryIR,
    ScopeIR,
    VerificationTask,
)
from dsl.ir.ir1.pretty import pretty_task
from dsl.language.vocabulary.operators import EnumComparisonOperator
from dsl.language.vocabulary.properties import EnumProperty
from dsl.semantic.types.enums import EnumDataType


def _task(comparison: ComparisonIR) -> VerificationTask:
    return VerificationTask(
        property_type=EnumProperty.ROBUSTNESS,
        backend=None,
        scope=ScopeIR(
            kind="pointwise",
            variables={"x0": "anchor"},
            neighborhood=None,
            domain=None,
        ),
        query=QueryIR(expression=comparison),
    )


def _comparison(feature_dtype: EnumDataType | None) -> ComparisonIR:
    return ComparisonIR(
        left=AttributeExpressionIR(
            entity="x0",
            feature="income",
            dtype=feature_dtype,
        ),
        op=EnumComparisonOperator.LTE,
        right=ConstantExpressionIR(value=1000, dtype=EnumDataType.INT),
    )


def test_pretty_task_prints_feature_dtype_when_present():
    output = pretty_task(_task(_comparison(EnumDataType.FLOAT)))

    assert "- x0.income : float <= 1000" in output


def test_pretty_task_keeps_existing_format_when_feature_dtype_is_absent():
    output = pretty_task(_task(_comparison(None)))

    assert "- x0.income <= 1000" in output
    assert "- x0.income : " not in output
