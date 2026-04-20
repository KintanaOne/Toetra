from lark import Tree
from forml.ast.nodes.implication import ImplicationNode
from forml.ast.nodes.property import PropertyNode
from forml.builder.backends import parse_backend
from forml.builder.core.utils import find_child, find_all_nodes, find_node
from forml.builder.core.ast_utils import node_value
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


def find_rhs_node(prop: Tree):
    for name in ["problem_expr", "logic_expr", "logic_not", "logic_or", "logic_and"]:
        node = find_node(prop, name)
        if node:
            return node
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
    right_node = find_rhs_node(prop)
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