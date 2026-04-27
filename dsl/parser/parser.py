from pathlib import Path
from lark import Lark

from test.fixtures.logic_samples import OPERATOR_PRECEDENCE_PROPERTY, SIMPLE_LOGIC_PROPERTY, VALID_IMPLICATION_PROPERTY, VALID_TRIPLE_OR_PROPERTY
from test.fixtures.program_samples import VALID_PROGRAM_WITH_BACKEND
from test.fixtures.properties_samples import VALID_AT_WITH_NEIGHBORHOOD, VALID_MINIMAL_EXISTS, VALID_MINIMAL_AT, VALID_MINIMAL_CHECK_AT, VALID_MINIMAL_PAIRWISE

# Load grammar file
GRAMMAR_PATH = "dsl/language/grammar/forml_grammar.lark"

with open(GRAMMAR_PATH, "r", encoding="utf-8") as f:
    grammar = f.read()

# Instantiate the parser
forml_parser = Lark(
    grammar,
    start="program",
    parser="lalr",
    propagate_positions=True,
    maybe_placeholders=True,
    cache=False
)


def parse_forml_code(code: str):
    """Parses the raw DSL code into a Lark tree"""
    return forml_parser.parse(code)

if __name__ == "__main__":
    forml = VALID_AT_WITH_NEIGHBORHOOD
    tree = parse_forml_code(forml)
    print(tree.pretty())
    print(tree)
