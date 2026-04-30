# /dsl/ir/run_ir.py

from dsl.builder.core import pretty
from dsl.ir.ir1.pretty import pretty_print_tasks
from dsl.parser.parser import parse_forml_code
from dsl.builder.program import parse_program
from dsl.semantic.tracer import ValidationTracer
from dsl.semantic.validator import FORMLValidator

from dsl.ir.ir1.translator import IRTranslator
from test.fixtures.logic_samples import NESTED_IMPLICATION_PROPERTY, PARENTHESES_PRECEDENCE_PROPERTY, VALID_TRIPLE_AND_PROPERTY
from test.fixtures.properties_samples import VALID_AT_WITH_NEIGHBORHOOD, VALID_CHECK_AT_WITH_COMPLEX_ASSERTION


def run_ir(source: str):
    """
    Full pipeline until IR generation.

    Steps:
        1. Parse (CST)
        2. Build AST
        3. Semantic validation
        4. Translate to IR
    """

    # ---------------------------
    # 1. Parse → CST
    # ---------------------------
    cst = parse_forml_code(source)

    # ---------------------------
    # 2. CST → AST
    # ---------------------------
    ast = parse_program(cst)

    # ---------------------------
    # 3. Semantic validation
    # ---------------------------
    FORMLValidator().validate(ast, tracer=ValidationTracer(enabled=True))

    # ---------------------------
    # 4. AST → IR
    # ---------------------------
    translator = IRTranslator()
    tasks = translator.translate(ast)

    return tasks


# -----------------------------------------------------------------------------
# QUICK TEST
# -----------------------------------------------------------------------------

if __name__ == "__main__":

    SAMPLE = PARENTHESES_PRECEDENCE_PROPERTY

    tasks = run_ir(SAMPLE)

    print("\n=== IR OUTPUT ===\n")

    pretty_print_tasks(tasks)