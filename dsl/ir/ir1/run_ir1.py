from dsl.ir.ir1.pretty import pretty_print_tasks
from dsl.parser.parser import parse_forml_code
from dsl.builder.program import parse_program
from dsl.semantic.runtime.tracer import ValidationTracer
from dsl.semantic.core.validator import FORMLValidator
from dsl.ir.ir1.translator import IRTranslator


DEFAULT_SAMPLE = """
model := "model.onnx"
target := MyTarget

[ROBUSTNESS]:
check_at x0 => (x0.a <= 1 OR x0.b <= 2) AND x0.c <= 3
"""


def run_ir(source: str):
    """
    Full pipeline until IR generation.

    Steps:
        1. Parse CST
        2. Build AST
        3. Semantic validation
        4. Translate to IR1
    """

    cst = parse_forml_code(source)
    ast = parse_program(cst)

    FORMLValidator().validate(
        ast,
        tracer=ValidationTracer(enabled=False),
    )

    translator = IRTranslator()
    return translator.translate(ast)


if __name__ == "__main__":
    tasks = run_ir(DEFAULT_SAMPLE)

    print("\n=== IR OUTPUT ===\n")
    pretty_print_tasks(tasks)