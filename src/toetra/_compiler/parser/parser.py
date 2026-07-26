from importlib.resources import files

from lark import Lark, Tree

GRAMMAR_RESOURCE = files("toetra._language.grammar").joinpath("toetra_grammar.lark")
grammar = GRAMMAR_RESOURCE.read_text(encoding="utf-8")

toetra_parser = Lark(
    grammar,
    start="program",
    parser="lalr",
    lexer="basic",
    propagate_positions=True,
    maybe_placeholders=True,
    cache=False,
)


def parse_toetra_code(code: str) -> Tree:
    """Parse raw Toetra Specification Language code into a Lark CST."""
    return toetra_parser.parse(code)


if __name__ == "__main__":
    sample = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 in neighborhood(L2, eps=0.01) => CLASSIFICATION.EQUAL() using Z3
    """

    tree = parse_toetra_code(sample)
    print(tree.pretty())
