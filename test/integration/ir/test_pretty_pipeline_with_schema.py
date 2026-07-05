from dsl.ir.ir1.pretty import pretty_task
from test.fixtures.ir_schema_aware.ir_helpers import translate_source
from test.fixtures.ir_schema_aware.samples import NESTED_TYPED_LOGIC
from test.fixtures.ir_schema_aware.schemas import make_schema


def test_pretty_output_displays_schema_aware_ir_types():
    tasks = translate_source(NESTED_TYPED_LOGIC, model_schema=make_schema())

    output = pretty_task(tasks[0])

    assert "- x0.age : int <= 30" in output
    assert "- x0.income : float >= 1000" in output
    assert "- x0.is_active : bool == True" in output
