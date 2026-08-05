from __future__ import annotations

from lark import Token, Tree

from toetra._compiler.ast.nodes.header import (
    HeaderNode,
    SpecificationConstantDeclarationNode,
)
from toetra._compiler.builder.core.ast_utils import (
    clean_string,
    node_value,
    parse_literal_value,
)
from toetra._compiler.builder.core.strict import require_node, require_value
from toetra._compiler.builder.core.utils import find_all_nodes, find_child

# ============================================================================
# HEADER PARSING
# ============================================================================
# This module extracts the header section of the DSL AST.
# It enforces strict validation: missing header fields are rejected early.
# ============================================================================


def get_header(tree: Tree) -> Tree:
    """Return a header subtree from either a program or header CST node."""
    if tree.data == "header":
        return tree
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


def parse_dataset(tree: Tree) -> str | None:
    """Parse the optional ``dataset := ...`` header declaration."""

    header = get_header(tree)
    dataset_declaration = find_child(header, "dataset_declaration")
    if dataset_declaration is None:
        return None

    dataset_node = require_node(
        find_child(dataset_declaration, "dataset"),
        "Dataset node not found",
    )
    return require_value(
        clean_string(node_value(dataset_node)),
        "Dataset declaration is missing or invalid",
    )


# ---------------------------------------------------------------------------


def parse_header(tree: Tree) -> HeaderNode:
    """
    Parse header node into a strict HeaderNode AST.
    """

    model = parse_model(tree)
    target = parse_target(tree)
    dataset = parse_dataset(tree)

    specification_constants = [
        _parse_specification_constant(declaration)
        for declaration in find_all_nodes(
            get_header(tree),
            "specification_constant_declaration",
        )
    ]

    return HeaderNode(
        model=model,
        target=target,
        dataset=dataset,
        specification_constants=specification_constants,
    )


def _parse_specification_constant(
    declaration: Tree,
) -> SpecificationConstantDeclarationNode:
    """Build one immutable literal declaration from its CST node."""
    identifier = require_node(
        find_child(declaration, "identifier"),
        "Specification constant identifier not found",
    )
    literal = require_node(
        find_child(declaration, "specification_constant_literal"),
        "Specification constant literal not found",
    )

    name = require_value(
        node_value(identifier),
        "Specification constant identifier is missing or invalid",
    )

    tokens = [
        str(token)
        for token in literal.scan_values(lambda value: isinstance(value, Token))
    ]

    if not tokens:
        raise ValueError(f"Specification constant '{name}' has no literal value")

    # Signed numeric literals are represented by two tokens (for example
    # ``-`` and ``0.1``). Boolean and string literals use a single token.
    raw_value = "".join(tokens)

    return SpecificationConstantDeclarationNode(
        name=name,
        value=parse_literal_value(raw_value),
    )
