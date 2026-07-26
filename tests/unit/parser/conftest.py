from __future__ import annotations

from collections.abc import Callable

import pytest
from lark import Token, Tree


@pytest.fixture
def single_cst_tree() -> Callable[[Tree, str], Tree]:
    """Return the unique CST node matching ``data``."""

    def _single_cst_tree(root: Tree, data: str) -> Tree:
        matches = list(root.find_data(data))
        assert len(matches) == 1, f"Expected one {data!r}, got {len(matches)}"
        return matches[0]

    return _single_cst_tree


@pytest.fixture
def first_cst_token() -> Callable[[Tree], Token]:
    """Return the first token contained in a CST node."""

    def _first_cst_token(node: Tree) -> Token:
        tokens = list(node.scan_values(lambda value: isinstance(value, Token)))
        assert tokens, f"Expected at least one token in {node.data}"
        return tokens[0]

    return _first_cst_token


@pytest.fixture
def cst_operator_values() -> Callable[[Tree, str], list[str]]:
    """Return operators preserved below CST nodes named ``data``."""

    def _first_token(node: Tree) -> Token:
        tokens = list(node.scan_values(lambda value: isinstance(value, Token)))
        assert tokens, f"Expected at least one token in {node.data}"
        return tokens[0]

    def _cst_operator_values(root: Tree, data: str) -> list[str]:
        return [str(_first_token(node)) for node in root.find_data(data)]

    return _cst_operator_values
