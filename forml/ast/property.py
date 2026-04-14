from lark import Tree
from forml.ast.abstractor import parse_abstractor
from forml.core.utils import find_child, find_all_nodes, find_node
from forml.core.ast_utils import node_value
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


def parse_property(prop: Tree):
    mode = detect_mode(prop)

    expr_map = {
        "quantifier": parse_quantifier,
        "at": parse_at,
        "pairwise": parse_pairwise,
        "check_at": parse_check_at
    }

    expr = expr_map.get(mode, lambda x: {}) (prop)

    return {
        "type": node_value(find_node(prop, "property_type")),
        "expr": {**expr},
        "assertion": parse_assertion(find_node(prop, "assertion")),
        "abstractor": parse_abstractor(find_node(prop, "abstractor"))
    }