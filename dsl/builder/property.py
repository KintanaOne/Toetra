from lark import Token, Tree
from dsl.ast.nodes.implication import ImplicationNode
from dsl.ast.nodes.property import PropertyNode
from dsl.builder.backends import parse_backend
from dsl.builder.core.utils import find_child, find_all_nodes, find_node
from dsl.builder.core.ast_utils import node_value
from .expressions import (
    parse_at,
    parse_pairwise,
    parse_check_at,
    parse_quantifier
)
from .assertion import parse_assertion


# ============================================================================
# PROPERTY CORE
# ============================================================================

def detect_mode(prop: Tree) -> str:
    if find_node(prop, "quantifier_expr"):
        return "quantifier"
    if find_node(prop, "at_expr"):
        return "at"
    if find_node(prop, "check_expr"):
        return "check_at"
    if find_node(prop, "pairwise_expr"):
        return "pairwise"
    return "unknown"


def extract_rhs(prop: Tree):
    """
    Extract RHS = node after '=>' at property level.
    """

    found_implies = False

    for child in prop.children:
        # detect =>
        if isinstance(child, Token) and child.value == "=>":
            found_implies = True
            continue

        # first Tree after =>
        if found_implies and isinstance(child, Tree):
            return child

    # fallback
    return None


def parse_property(prop: Tree) -> PropertyNode:
    mode = detect_mode(prop)

    expr_map = {
        "at": parse_at,
        "pairwise": parse_pairwise,
        "check_at": parse_check_at,
        "quantifier": parse_quantifier,
    }

    left = expr_map.get(mode, lambda x: None)(prop)

    # 🔥 RIGHT SIDE OF "=>"
    right_node = extract_rhs(prop)
    right = parse_assertion(right_node)

    # 🔥 BACKEND
    backend = parse_backend(find_node(prop, "backend"))

    return PropertyNode(
        type=node_value(find_node(prop, "property_type")),
        implication=ImplicationNode(
            left=left,
            right=right
        ),
        backend=backend
    )