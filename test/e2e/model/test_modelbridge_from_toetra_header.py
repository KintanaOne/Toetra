from dsl.builder.program import parse_program
from dsl.parser.parser import parse_toetra_code
from dsl.semantic.core.validator import ToetraValidator
from dsl.semantic.runtime.tracer import ValidationTracer
from model.runtime.manager import ModelManager
from test.fixtures.model_bridge.factories import (
    dataset_path,
    make_classification_joblib,
)


def test_toetra_header_target_is_used_by_modelbridge_end_to_end(tmp_path):
    model_path = make_classification_joblib(tmp_path)

    source = f"""
model := "{model_path.as_posix()}"
target := MyTarget

[ROBUSTNESS]:
forall x0 => x0.age >= 0
"""

    cst = parse_toetra_code(source)
    ast = parse_program(cst)

    ToetraValidator().validate(ast, tracer=ValidationTracer(enabled=False))

    schema = ModelManager(
        model_path=ast.header.model,
        dataset_path=dataset_path("classification.csv"),
        target_name=ast.header.target,
    ).build_schema()

    assert schema.target == "MyTarget"
    assert "MyTarget" not in schema.features
    assert set(schema.features) == {"age", "income", "score"}
