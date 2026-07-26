from typing import TypeVar, Optional
from lark import Tree

from toetra._compiler.builder.core.utils import find_node

T = TypeVar("T")


# ============================================================================
# STRICT VALIDATION HELPERS
# ============================================================================
# These helpers ensure that no None values leak from the parsing layer
# into the AST / domain layer.
#
# The goal is to enforce strong invariants at the boundary between:
#   - Lark parsing (which is permissive and optional-heavy)
#   - Domain AST construction (which must be strict and type-safe)
#
# This avoids repetitive None-checking across all parser functions.
# ============================================================================


def require_node(node: Optional[T], message: str) -> T:
    """
    Ensures that a parsed node is not None.

    Args:
        node: potentially None node returned by a search function
        message: error message used if the node is missing

    Returns:
        A non-None node (type-safe)

    Raises:
        ValueError: if node is None
    """
    if node is None:
        raise ValueError(message)
    return node


def require_tree(node: Optional[Tree], message: str) -> Tree:
    """
    Strict version specialized for Lark Tree nodes.

    Ensures the parser does not propagate missing tree nodes.
    """
    if node is None:
        raise ValueError(message)
    return node


def require_value(value: Optional[str], message: str) -> str:
    """
    Ensures that extracted token values are not None.

    Used after node_value(...) calls.
    """
    if value is None:
        raise ValueError(message)
    return value


def optional(node, name, parser):
    child = find_node(node, name)
    return parser(child) if child else None


def safe_find_child(tree: Tree, name: str) -> Tree:
    """
    Safe wrapper around find_child.

    Guarantees that the returned child node exists.
    """
    from toetra._compiler.builder.core.utils import find_child

    node = find_child(tree, name)
    return require_tree(node, f"Expected child node '{name}' not found")


def safe_find_node(tree: Tree, name: str) -> Tree:
    """
    Safe wrapper around find_node.

    Guarantees that the requested node exists in the tree.
    """
    from toetra._compiler.builder.core.utils import find_node

    node = find_node(tree, name)
    return require_tree(node, f"Expected node '{name}' not found")
