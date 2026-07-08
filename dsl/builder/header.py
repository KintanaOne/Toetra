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
    return require_node(find_child(tree, "header"), "Header node not found")


# ---------------------------------------------------------------------------


def parse_model(tree: Tree) -> str:
    """
    Parse:
        model := "path"
    """

    header = get_header(tree)

    model_declaration = require_node(
        find_child(header, "model_declaration"),
        "Model declaration not found",
    )

    model_node = require_node(
        find_child(model_declaration, "model"),
        "Model node not found",
    )

    return require_value(
        clean_string(node_value(model_node)),
        "Model declaration is missing or invalid",
    )


# ---------------------------------------------------------------------------


def parse_target(tree: Tree) -> str:
    """
    Parse:
        target := Column
    """

    header = get_header(tree)

    target_declaration = require_node(
        find_child(header, "target_declaration"),
        "Target declaration not found",
    )

    identifier_node = require_node(
        find_child(target_declaration, "identifier"),
        "Target identifier not found",
    )

    return require_value(
        clean_string(node_value(identifier_node)),
        "Target declaration is missing or invalid",
    )


# ---------------------------------------------------------------------------


def parse_header(tree: Tree) -> HeaderNode:
    """
    Parse header node into a strict HeaderNode AST.
    """

    model = parse_model(tree)
    target = parse_target(tree)

    return HeaderNode(model=model, target=target)
