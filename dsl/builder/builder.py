from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from test.fixtures.properties_samples import VALID_CHECK_AT_WITH_COMPLEX_ASSERTION, VALID_FORALL_WITH_DOMAIN
from test.fixtures.logic_samples import OPERATOR_PRECEDENCE_PROPERTY

if __name__ == "__main__":
    """ This script is for quick testing of the builder. It parses a sample property and prints the resulting AST """
    CST = parse_forml_code(VALID_CHECK_AT_WITH_COMPLEX_ASSERTION)
    print(CST.pretty())

    AST = parse_program(CST)
    print(AST)