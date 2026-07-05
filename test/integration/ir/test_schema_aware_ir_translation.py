from dsl.semantic.types.enums import EnumDataType
from test.fixtures.ir_schema_aware.ir_helpers import comparison_by_feature, translate_source
from test.fixtures.ir_schema_aware.samples import NESTED_TYPED_LOGIC
from test.fixtures.ir_schema_aware.schemas import make_schema


def test_schema_aware_semantic_validation_feeds_typed_ir_for_nested_logic():
    tasks = translate_source(NESTED_TYPED_LOGIC, model_schema=make_schema())

    comparisons = comparison_by_feature(tasks[0])

    assert set(comparisons) == {"age", "income", "is_active"}

    assert comparisons["age"].entity == "x0"
    assert comparisons["age"].feature_dtype is EnumDataType.INT
    assert comparisons["age"].value_dtype is EnumDataType.INT

    assert comparisons["income"].entity == "x0"
    assert comparisons["income"].feature_dtype is EnumDataType.FLOAT
    assert comparisons["income"].value_dtype is EnumDataType.INT

    assert comparisons["is_active"].entity == "x0"
    assert comparisons["is_active"].feature_dtype is EnumDataType.BOOL
    assert comparisons["is_active"].value_dtype is EnumDataType.BOOL


def test_typed_ir_translation_keeps_scope_variables():
    tasks = translate_source(NESTED_TYPED_LOGIC, model_schema=make_schema())

    task = tasks[0]

    assert task.scope.kind == "pointwise"
    assert task.scope.variables == {"x0": "anchor"}
