from __future__ import annotations

from lark import Tree
from dsl.ast.nodes.header import HeaderNode
from dsl.builder.core.utils import find_child
from dsl.builder.core.ast_utils import node_value, clean_string
from dsl.builder.core.strict import require_node, require_value


# ============================================================================
# HEADER PARSING
# ============================================================================
# This module extracts the header section of the DSL AST.
# It enforces strict validation: missing header fields are rejected early.
# ============================================================================


def get_header(tree: Tree) -> Tree:
    """
    Extract header node from full AST.
    """
    return require_node(
        find_child(tree, "header"),
        "Header node not found"
    )


# ---------------------------------------------------------------------------

def parse_model(tree: Tree) -> str:
    """
    model := "path"
    """

    header = get_header(tree)

    model_node = find_child(header, "model_declaration")

    return require_value(
        clean_string(node_value(model_node)),
        "Model declaration is missing or invalid"
    )


# ---------------------------------------------------------------------------

def parse_target(tree: Tree) -> str:
    """
    target := Column
    """

    header = get_header(tree)

    target_node = find_child(header, "target_declaration")

    return require_value(
        clean_string(node_value(target_node)),
        "Target declaration is missing or invalid"
    )


# ---------------------------------------------------------------------------

def parse_header(tree: Tree) -> HeaderNode:
    """
    Parse header node into a strict HeaderNode AST.
    """

    header_tree = get_header(tree)

    model = parse_model(header_tree)
    target = parse_target(header_tree)

    return HeaderNode(
        model=model,
        target=target
    )