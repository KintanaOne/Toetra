from __future__ import annotations

from typing import TYPE_CHECKING

from dsl.builder.program import parse_program
from dsl.ir.ir1.pretty import pretty_print_tasks
from dsl.ir.ir1.translator import IRTranslator
from dsl.parser.parser import parse_forml_code
from dsl.semantic.core.validator import FORMLValidator
from dsl.semantic.runtime.tracer import ValidationTracer

if TYPE_CHECKING:
    from model.schema.model_schema import ModelSchema

DEFAULT_SAMPLE = """
model := "model.onnx"
target := MyTarget

[ROBUSTNESS]:
check_at x0 => (x0.a <= 1 OR x0.b <= 2) AND x0.c <= 3
"""


def run_ir(
    source: str,
    *,
    model_schema: ModelSchema | None = None,
):
    """Run the complete source-to-IR1 pipeline.

    When a ``ModelSchema`` is available it is passed through semantic
    validation so input features and the model target retain their normalized
    dtypes in IR1. Callers without a model schema keep the permissive historical
    behavior.
    """

    cst = parse_forml_code(source)
    ast = parse_program(cst)

    FORMLValidator().validate(
        ast,
        tracer=ValidationTracer(enabled=False),
        model_schema=model_schema,
    )

    translator = IRTranslator()
    return translator.translate(ast)


if __name__ == "__main__":
    tasks = run_ir(DEFAULT_SAMPLE)

    print("\n=== IR OUTPUT ===\n")
    pretty_print_tasks(tasks)
