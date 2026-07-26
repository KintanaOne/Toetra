from toetra._compiler.ir.ir1.nodes import (
    AttributeExpressionIR,
    ComparisonIR,
    ConstantExpressionIR,
)
from toetra._compiler.semantic.types.enums import EnumDataType
from tests.support.ir_serialization import translate_source
from tests.fixtures.ir_schema_aware.samples import (
    CHECK_AT_BOOL_FEATURE,
    CHECK_AT_IMPLICIT_AGE,
    CHECK_AT_INCOME,
    FORALL_IMPLICIT_AGE,
)
from tests.support.schemas import make_schema


def _assert_attribute_constant_comparison(
    comparison: ComparisonIR,
    *,
    entity: str,
    feature: str,
    feature_dtype: EnumDataType | None,
    value: object,
    value_dtype: EnumDataType,
) -> None:
    assert isinstance(comparison.left, AttributeExpressionIR)
    assert comparison.left.entity == entity
    assert comparison.left.feature == feature
    assert comparison.left.dtype is feature_dtype

    assert isinstance(comparison.right, ConstantExpressionIR)
    assert comparison.right.value == value
    assert comparison.right.dtype is value_dtype


def test_ir_comparison_contains_operand_dtypes_when_schema_is_provided():
    comparison = translate_source(CHECK_AT_INCOME, model_schema=make_schema())[
        0
    ].query.expression

    assert isinstance(comparison, ComparisonIR)
    _assert_attribute_constant_comparison(
        comparison,
        entity="x0",
        feature="income",
        feature_dtype=EnumDataType.FLOAT,
        value=1000,
        value_dtype=EnumDataType.INT,
    )


def test_ir_attribute_dtype_is_none_without_schema():
    comparison = translate_source(CHECK_AT_INCOME)[0].query.expression

    assert isinstance(comparison, ComparisonIR)
    _assert_attribute_constant_comparison(
        comparison,
        entity="x0",
        feature="income",
        feature_dtype=None,
        value=1000,
        value_dtype=EnumDataType.INT,
    )


def test_ir_uses_semantic_resolution_for_implicit_attribute_with_schema():
    comparison = translate_source(CHECK_AT_IMPLICIT_AGE, model_schema=make_schema())[
        0
    ].query.expression

    assert isinstance(comparison, ComparisonIR)
    _assert_attribute_constant_comparison(
        comparison,
        entity="x0",
        feature="age",
        feature_dtype=EnumDataType.INT,
        value=30,
        value_dtype=EnumDataType.INT,
    )


def test_ir_uses_symbolic_entity_for_quantifier_with_schema():
    comparison = translate_source(FORALL_IMPLICIT_AGE, model_schema=make_schema())[
        0
    ].query.expression

    assert isinstance(comparison, ComparisonIR)
    _assert_attribute_constant_comparison(
        comparison,
        entity="x0",
        feature="age",
        feature_dtype=EnumDataType.INT,
        value=30,
        value_dtype=EnumDataType.INT,
    )


def test_ir_preserves_bool_feature_and_bool_value_dtype():
    comparison = translate_source(CHECK_AT_BOOL_FEATURE, model_schema=make_schema())[
        0
    ].query.expression

    assert isinstance(comparison, ComparisonIR)
    _assert_attribute_constant_comparison(
        comparison,
        entity="x0",
        feature="is_active",
        feature_dtype=EnumDataType.BOOL,
        value=True,
        value_dtype=EnumDataType.BOOL,
    )
