from __future__ import annotations

from dataclasses import dataclass

from lark import Tree


@dataclass(frozen=True)
class SourceSpan:
    """Half-open source range attached to one AST node."""

    line: int
    column: int
    end_line: int
    end_column: int


def source_span_from_tree(tree: Tree) -> SourceSpan | None:
    """Build a source span from Lark metadata when positions are available."""
    meta = tree.meta
    line = getattr(meta, "line", None)
    column = getattr(meta, "column", None)
    end_line = getattr(meta, "end_line", None)
    end_column = getattr(meta, "end_column", None)

    if not all(
        isinstance(value, int) for value in (line, column, end_line, end_column)
    ):
        return None

    assert isinstance(line, int)
    assert isinstance(column, int)
    assert isinstance(end_line, int)
    assert isinstance(end_column, int)

    return SourceSpan(
        line=line,
        column=column,
        end_line=end_line,
        end_column=end_column,
    )
