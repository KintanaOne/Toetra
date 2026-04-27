from lark import Token, Tree
from dsl.ast.nodes.assertion import AssertionNode
from dsl.ast.nodes.property import PropertyNode, PropertyRuleNode
from dsl.builder.backends import parse_backend
from dsl.builder.core.strict import require_node, require_value
from dsl.builder.core.utils import find_child, find_node
from dsl.builder.core.ast_utils import node_value
from .expressions import (
    parse_at,
    parse_pairwise,
    parse_check_at,
    parse_quantifier
)
from .assertion import parse_assertion


# ============================================================================
# PROPERTY CORE PARSING
# ============================================================================
# This module parses full property definitions:
#   - LHS (expression)
#   - RHS (assertion after =>)
#   - backend configuration
# ============================================================================


# ---------------------------------------------------------------------------
# Mode detection
# ---------------------------------------------------------------------------

def detect_mode(prop: Tree) -> str:
    """
    Detect which expression type is used in the property LHS.
    """

    if find_node(prop, "quantifier_expr"):
        return "quantifier"
    if find_node(prop, "at_expr"):
        return "at"
    if find_node(prop, "check_expr"):
        return "check_at"
    if find_node(prop, "pairwise_expr"):
        return "pairwise"

    return "unknown"


# ---------------------------------------------------------------------------
# RHS extraction
# ---------------------------------------------------------------------------

from lark import Tree, Token


def extract_rhs(prop: Tree) -> Tree:
    """
    Extract RHS expression from property.

    IMPORTANT:
    Lark inline-expands 'assertion', so RHS is directly a logic_* node
    (e.g. logic_or, logic_and), not an 'assertion' node.
    """

    found_imply = False

    property = prop.children[0]

    for child in property.children:

        # skip metadata nodes
        if isinstance(child, Tree) and child.data in (
            "property_type",
            "property_expr",
        ):
            continue

        # detect implication separator
        if isinstance(child, Tree) and child.data == "property_imply":
            found_imply = True
            continue

        # RHS = first real logic subtree AFTER implication
        if found_imply and isinstance(child, Tree):
            return child

    raise ValueError("Missing RHS in property")

# ---------------------------------------------------------------------------
# Main parser
# ---------------------------------------------------------------------------

def parse_property(prop: Tree) -> PropertyNode:
    """
    Parse full property AST into PropertyNode.
    """

    mode = detect_mode(prop)

    expr_map = {
        "at": parse_at,
        "pairwise": parse_pairwise,
        "check_at": parse_check_at,
        "quantifier": parse_quantifier,
    }

    if mode not in expr_map:
        raise ValueError(f"Unknown property mode: {mode}")

    # -----------------------------------------------------------------------
    # Parse LHS expression
    # -----------------------------------------------------------------------
    
    left = expr_map[mode](prop)

    # -----------------------------------------------------------------------
    # Parse RHS assertion
    # -----------------------------------------------------------------------
    
    right_node = extract_rhs(prop)

    logical_root = parse_assertion(right_node)

    right = AssertionNode(root=logical_root)

    # -----------------------------------------------------------------------
    # Parse backend configuration (strict)
    # -----------------------------------------------------------------------
    
    backend_node = find_node(prop, "backend")
    backend = parse_backend(backend_node)

    # -----------------------------------------------------------------------
    # Property type (strict extraction)
    # -----------------------------------------------------------------------
    property_type_node = find_node(prop, "property_type")

    property_type = require_value(
        node_value(property_type_node),
        "Property type is missing"
    )

    # -----------------------------------------------------------------------
    # Build AST
    # -----------------------------------------------------------------------
    return PropertyNode(
        type=property_type,
        rule=PropertyRuleNode(
            scope=left,
            assertion=right
        ),
        backend=backend
    )