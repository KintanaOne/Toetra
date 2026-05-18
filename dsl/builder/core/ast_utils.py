from __future__ import annotations

from lark import Tree, Token

from dsl.ast.nodes.primitives import AttributeNode, ConstantNode, EnumDataType
from dsl.builder.core.types import LarkNode
from dsl.builder.core.utils import get_token_value

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
    Parse an attribute expression into an AttributeNode.

    Supported forms:
    - age
    - x0.age
    - user.profile.age
    - a.b.c.d

    Design rules:
    - Last identifier = feature
    - First identifier (if multiple) = entity
    - Full chain stored in `path`
    """

    def require_str(value: str | None) -> str:
        if value is None:
            raise ValueError("Expected string, got None")
        return value

    identifiers = [
        require_str(get_token_value(child))
        for child in node.children
        if isinstance(child, Tree) and child.data == "identifier"
    ]

    identifiers = [i for i in identifiers if i is not None]

    if not identifiers:
        raise ValueError("Invalid attribute: no identifiers found")

    return AttributeNode(
        entity=identifiers[0] if len(identifiers) > 1 else None,
        feature=identifiers[-1],
        path=identifiers,
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
