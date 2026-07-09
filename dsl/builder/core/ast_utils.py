from __future__ import annotations

from lark import Tree, Token

from dsl.ast.nodes.primitives import AttributeNode, ConstantNode, EnumDataType
from dsl.builder.core.lark_types import LarkNode
from dsl.builder.core.utils import get_node_name_or_value, get_token_value

# ============================================================================
# GENERIC NODE VALUE EXTRACTION
# ============================================================================
# These helpers provide a uniform way to extract meaningful values
# from Lark nodes without relying on grammar-specific positions.


def node_value(node: LarkNode | None) -> str | None:
    """
    Recursively extract the first usable string value from a node.

    Rules:
    - Token -> return value
    - Tree -> recursively inspect children
    - None -> return None

    This function avoids hardcoding grammar structure elsewhere.
    """
    if node is None:
        return None

    if isinstance(node, Token):
        return node.value

    if isinstance(node, Tree):
        for child in node.children:
            v = node_value(child)
            if v is not None:
                return v

    return None


# ============================================================================
# STRING NORMALIZATION
# ============================================================================


def clean_string(value: str | None) -> str | None:
    """
    Normalize string literals by removing surrounding quotes.

    Supports:
    - "text"
    - 'text'
    """
    if value is None:
        return None

    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]

    return value


# ============================================================================
# ATTRIBUTE PARSING
# ============================================================================
# Converts a Lark subtree into a structured AttributeNode.


def parse_attribute(node: Tree) -> AttributeNode:
    """
    Parse:
        x.a
        target
        x.a.b

    First segment must be a normal identifier.
    Following segments may be soft identifiers, including protected words
    such as target.
    """

    parts: list[str] = []

    for child in node.children:
        if not isinstance(child, Tree):
            continue

        if child.data in {"identifier", "attribute_identifier"}:
            value = get_node_name_or_value(child)
            if value is not None:
                parts.append(value)

    if not parts:
        raise ValueError("Invalid attribute")

    if len(parts) == 1:
        return AttributeNode(
            entity=None,
            feature=parts[0],
            path=parts,
        )

    return AttributeNode(
        entity=parts[0],
        feature=".".join(parts[1:]),
        path=parts,
    )


# ============================================================================
# CONSTANT PARSING
# ============================================================================
# Converts raw tokens into typed ConstantNode.


def parse_value(node: Tree) -> ConstantNode:
    """
    Parse a value node into a ConstantNode with inferred type.

    Type inference strategy:
    1. Try int
    2. Try float
    3. Fallback to string
    """
    raw = get_token_value(node)

    if raw is None:
        raw = get_node_name_or_value(node)

    if raw is None:
        raise ValueError("Invalid value node")

    cleaned = clean_string(raw)

    if cleaned is None:
        raise ValueError("Invalid value: None after cleaning")

    if cleaned.lower() == "true":
        return ConstantNode(True, EnumDataType.BOOL)

    if cleaned.lower() == "false":
        return ConstantNode(False, EnumDataType.BOOL)

    if cleaned.lower() == "null":
        return ConstantNode(None, EnumDataType.NoneType)

    # Integer parsing
    try:
        return ConstantNode(value=int(cleaned), dtype=EnumDataType.INT)
    except (ValueError, TypeError):
        pass

    # Float parsing
    try:
        return ConstantNode(value=float(cleaned), dtype=EnumDataType.FLOAT)
    except (ValueError, TypeError):
        pass

    # Fallback: string
    return ConstantNode(value=cleaned, dtype=EnumDataType.STRING)


# ============================================================================
# TREE NORMALIZATION
# ============================================================================
# Removes syntactic noise from Lark trees.


def unwrap_single_child(node: Tree) -> Tree:
    """
    Collapse intermediate nodes that only wrap a single child.

    This is a purely syntactic normalization step:
    - No semantic assumption
    - Safe to apply globally

    Useful to simplify AST construction logic.
    """
    while (
        isinstance(node, Tree)
        and len(node.children) == 1
        and isinstance(node.children[0], Tree)
    ):
        node = node.children[0]

    return node
