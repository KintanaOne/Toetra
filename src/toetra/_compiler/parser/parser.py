from importlib.resources import files

from lark import Lark, Token, Tree
from lark.exceptions import (
    UnexpectedCharacters,
    UnexpectedEOF,
    UnexpectedInput,
    UnexpectedToken,
)

from toetra._compiler.parser.errors import ParserError

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
    try:
        return toetra_parser.parse(code)
    except UnexpectedInput as error:
        raise _parser_error(error) from error


def _parser_error(error: UnexpectedInput) -> ParserError:
    line = getattr(error, "line", None)
    column = getattr(error, "column", None)
    location = _location_suffix(line, column)

    if isinstance(error, UnexpectedCharacters):
        character = getattr(error, "char", None)
        rendered = repr(character) if character is not None else "an invalid character"
        return ParserError(
            f"Unexpected character {rendered}{location}.",
            code="PARSER_UNEXPECTED_CHARACTER",
            hint="Check the Toetra syntax near this location.",
            line=line,
            column=column,
        )

    if isinstance(error, UnexpectedEOF) or (
        isinstance(error, UnexpectedToken) and _is_end_token(error.token)
    ):
        return ParserError(
            f"Unexpected end of specification{location}.",
            code="PARSER_UNEXPECTED_END_OF_INPUT",
            hint="Complete the declaration or expression before the end of the file.",
            line=line,
            column=column,
        )

    if isinstance(error, UnexpectedToken):
        return ParserError(
            f"Unexpected token {error.token.value!r}{location}.",
            code="PARSER_UNEXPECTED_TOKEN",
            hint="Check the Toetra syntax near this token.",
            line=line,
            column=column,
        )

    return ParserError(
        f"Invalid Toetra syntax{location}.",
        hint="Check the Toetra syntax near this location.",
        line=line,
        column=column,
    )


def _is_end_token(token: Token) -> bool:
    return token.type == "$END"


def _location_suffix(line: int | None, column: int | None) -> str:
    if line is not None and column is not None:
        return f" at line {line}, column {column}"
    if line is not None:
        return f" at line {line}"
    return ""


if __name__ == "__main__":
    sample = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 in neighborhood(L2, eps=0.01) => CLASSIFICATION.EQUAL() using Z3
    """

    tree = parse_toetra_code(sample)
    print(tree.pretty())
