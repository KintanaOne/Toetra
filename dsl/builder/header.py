from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Union

from lark import Tree
from dsl.builder.core.utils import find_child
from dsl.builder.core.ast_utils import node_value, clean_string

from dsl.ast.nodes.header import HeaderNode


# ============================================================================
# HEADER PARSING
# ============================================================================

def get_header(tree: Tree) -> Tree:
    return find_child(tree, "header")


def parse_model(tree: Tree) -> str:
    """
    model := "path"
    """
    return clean_string(node_value(find_child(get_header(tree), "model_declaration")))


def parse_target(tree: Tree) -> str:
    """
    target := Column
    """
    return clean_string(node_value(find_child(get_header(tree), "target_declaration")))


def parse_header(tree: Tree) -> HeaderNode:
    """
    Parse header node into HeaderNode.
    """
    header_tree = get_header(tree)

    if not header_tree:
        raise ValueError("Header node not found in AST")

    model = parse_model(header_tree)
    target = parse_target(header_tree)

    return HeaderNode(model=model, target=target)