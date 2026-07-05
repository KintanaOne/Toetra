from dsl.ir.ir1.nodes import ComparisonIR
from dsl.semantic.types.enums import EnumDataType
from test.fixtures.ir_schema_aware.ir_helpers import translate_source
from test.fixtures.ir_schema_aware.samples import (
    CHECK_AT_BOOL_FEATURE,
    CHECK_AT_IMPLICIT_AGE,
    CHECK_AT_INCOME,
    FORALL_IMPLICIT_AGE,
)
from test.fixtures.ir_schema_aware.schemas import make_schema


def test_ir_comparison_contains_feature_dtype_when_schema_is_provided():
    tasks = translate_source(CHECK_AT_INCOME, model_schema=make_schema())

    comparison = tasks[0].query.expression

    assert isinstance(comparison, ComparisonIR)
    assert comparison.entity == "x0"
    assert comparison.feature == "income"
    assert comparison.feature_dtype is EnumDataType.FLOAT
    assert comparison.value_dtype is EnumDataType.INT
    assert comparison.value == 1000


def test_ir_comparison_dtype_is_none_without_schema():
    tasks = translate_source(CHECK_AT_INCOME)

    comparison = tasks[0].query.expression

    assert isinstance(comparison, ComparisonIR)
    assert comparison.entity == "x0"
    assert comparison.feature == "income"
    assert comparison.feature_dtype is None
    assert comparison.value_dtype is EnumDataType.INT


def test_ir_uses_semantic_resolution_for_implicit_attribute_with_schema():
    tasks = translate_source(CHECK_AT_IMPLICIT_AGE, model_schema=make_schema())

    comparison = tasks[0].query.expression

    assert isinstance(comparison, ComparisonIR)
    assert comparison.entity == "x0"
    assert comparison.feature == "age"
    assert comparison.feature_dtype is EnumDataType.INT
    assert comparison.value_dtype is EnumDataType.INT


def test_ir_uses_symbolic_entity_for_quantifier_with_schema():
    tasks = translate_source(FORALL_IMPLICIT_AGE, model_schema=make_schema())

    comparison = tasks[0].query.expression

    assert isinstance(comparison, ComparisonIR)
    assert comparison.entity == "_x"
    assert comparison.feature == "age"
    assert comparison.feature_dtype is EnumDataType.INT
    assert comparison.value_dtype is EnumDataType.INT


def test_ir_preserves_bool_feature_and_bool_value_dtype():
    tasks = translate_source(CHECK_AT_BOOL_FEATURE, model_schema=make_schema())

    comparison = tasks[0].query.expression

    assert isinstance(comparison, ComparisonIR)
    assert comparison.entity == "x0"
    assert comparison.feature == "is_active"
    assert comparison.feature_dtype is EnumDataType.BOOL
    assert comparison.value_dtype is EnumDataType.BOOL
    assert comparison.value is True
