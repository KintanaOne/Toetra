from dsl.ir.ir1.nodes import ComparisonIR, QueryIR, ScopeIR, VerificationTask
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


def test_pretty_task_prints_feature_dtype_when_present():
    comparison = ComparisonIR(
        entity="x0",
        feature="income",
        op=EnumComparisonOperator.LTE,
        value=1000,
        feature_dtype=EnumDataType.FLOAT,
        value_dtype=EnumDataType.INT,
    )

    output = pretty_task(_task(comparison))

    assert "- x0.income : float <= 1000" in output


def test_pretty_task_keeps_existing_format_when_feature_dtype_is_absent():
    comparison = ComparisonIR(
        entity="x0",
        feature="income",
        op=EnumComparisonOperator.LTE,
        value=1000,
        feature_dtype=None,
        value_dtype=EnumDataType.INT,
    )

    output = pretty_task(_task(comparison))

    assert "- x0.income <= 1000" in output
    assert "- x0.income : " not in output
