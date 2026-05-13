from dsl.builder.core.pretty_ast import pretty

from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from test.fixtures.properties_samples import VALID_AT_WITH_NEIGHBORHOOD, VALID_CHECK_AT_WITH_COMPLEX_ASSERTION, VALID_FORALL_WITH_DOMAIN, VALID_MINIMAL_AT, VALID_MINIMAL_CHECK_AT
from test.fixtures.logic_samples import OPERATOR_PRECEDENCE_PROPERTY

if __name__ == "__main__":
    """ This script is for quick testing of the builder. It parses a sample property and prints the resulting AST """
    # LARK
    CST = parse_forml_code(VALID_MINIMAL_CHECK_AT)
    print(CST.pretty())

    # BUILDER
    AST = parse_program(CST)
    print(pretty(AST))