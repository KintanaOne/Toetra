from dsl.builder.core.pretty_ast import pretty

from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from test.fixtures.program_samples import VALID_PROGRAM_WITH_BACKEND

if __name__ == "__main__":
    """This script is for quick testing of the builder. It parses a sample property and prints the resulting AST"""
    # LARK
    CST = parse_forml_code(VALID_PROGRAM_WITH_BACKEND)
    print(CST.pretty())

    # BUILDER
    AST = parse_program(CST)
    print((AST))
