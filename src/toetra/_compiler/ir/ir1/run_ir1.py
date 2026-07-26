from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from toetra._compiler.builder.program import parse_program
from toetra._compiler.ir.ir1.pretty import pretty_print_tasks
from toetra._compiler.ir.ir1.translator import IRTranslator
from toetra._compiler.parser.parser import parse_toetra_code
from toetra._compiler.semantic.core.validator import ToetraValidator
from toetra._compiler.semantic.runtime.tracer import ValidationTracer

if TYPE_CHECKING:
    from toetra._models.schema.model_schema import ModelSchema
    from toetra._compiler.semantic.symbols.point import ResolvedAnchorBinding

DEFAULT_SAMPLE = """
model := "model.onnx"
target := MyTarget

[ROBUSTNESS]:
forall x0 => (x0.a <= 1 OR x0.b <= 2) AND x0.c <= 3
"""


def run_ir(
    source: str,
    *,
    model_schema: ModelSchema | None = None,
    resolved_anchors: Mapping[str, ResolvedAnchorBinding] | None = None,
):
    """Run the complete source-to-IR1 pipeline.

    When a ``ModelSchema`` is available it is passed through semantic
    validation so input features and the model target retain their normalized
    dtypes in IR1. Callers without a model schema keep the permissive historical
    behavior.
    """

    cst = parse_toetra_code(source)
    ast = parse_program(cst)

    ToetraValidator().validate(
        ast,
        tracer=ValidationTracer(enabled=False),
        model_schema=model_schema,
        resolved_anchors=resolved_anchors,
    )

    translator = IRTranslator()
    return translator.translate(ast)


if __name__ == "__main__":
    tasks = run_ir(DEFAULT_SAMPLE)

    print("\n=== IR OUTPUT ===\n")
    pretty_print_tasks(tasks)
