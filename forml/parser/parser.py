# forml/parser/forml_parser.py

from pathlib import Path
from lark import Lark

# Load grammar file
GRAMMAR_PATH = Path(__file__).parent.parent / "grammar/forml_grammar.lark"

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
    test_path = Path(__file__).parent.parent / "example/00_simple_correct_example.forml"
    print(test_path)
    if test_path.exists():
        with open(test_path, "r", encoding="utf-8") as f:
            code = f.read()
        tree = parse_forml_code(code)
        print(tree.pretty())
    else:
        print("No example.forml file found.")
