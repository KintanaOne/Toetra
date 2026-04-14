from lark import Tree
from forml.core.utils import find_child, find_node
from forml.core.ast_utils import node_value
from .domain import parse_domain
from .neighborhood import parse_neighborhood


# ============================================================================
# EXPRESSIONS (AT / CHECK / PAIRWISE / QUANTIFIER)
# ============================================================================

def parse_at(prop: Tree):
    node = find_node(prop, "at_expr")

    return {
        "kind": "at",
        "variable": node_value(find_child(node, "identifier")),
        "neighborhood": parse_neighborhood(node),
        "domain": parse_domain(node),
    }


def parse_pairwise(prop: Tree):
    node = find_node(prop, "pairwise_expr")

    return {
        "kind": "pairwise",
        "pair": node_value(find_child(node, "pairwise_token")),
        "neighborhood": parse_neighborhood(node),
        "domain": parse_domain(node),
    }


def parse_check_at(prop: Tree):
    node = find_node(prop, "check_expr")

    return {
        "kind": "check_at",
        "variable": node_value(find_child(node, "identifier"))
    }


def parse_quantifier(prop: Tree):
    q = find_node(prop, "quantifier_expr")

    return {
        "kind": "quantifier",
        "quantifier": node_value(q),
        "domain": parse_domain(prop),
    }