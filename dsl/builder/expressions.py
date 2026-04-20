from lark import Tree
from dsl.ast.nodes.expressions import (
    AtExprNode, 
    CheckAtExprNode, 
    PairwiseExprNode,
    QuantifierExprNode
)
from dsl.builder.core.utils import find_child, find_node
from dsl.builder.core.ast_utils import node_value
from dsl.builder.domain import parse_domain
from dsl.builder.neighborhood import parse_neighborhood


# ============================================================================
# EXPRESSIONS (AT / CHECK / PAIRWISE / QUANTIFIER)
# ============================================================================

def parse_at(prop: Tree) -> AtExprNode:
    node = find_node(prop, "at_expr")

    return AtExprNode(
        variable=node_value(find_child(node, "identifier")),
        neighborhood=parse_neighborhood(node),
        domain=parse_domain(node),
    )


def parse_pairwise(prop: Tree) -> PairwiseExprNode:
    node = find_node(prop, "pairwise_expr")

    return PairwiseExprNode(
        pair=node_value(find_child(node, "pairwise_token")),
        neighborhood=parse_neighborhood(node),
        domain=parse_domain(node)
    )

def parse_check_at(prop: Tree) -> CheckAtExprNode:
    node = find_node(prop, "check_expr")

    return CheckAtExprNode(
        variable=node_value(find_child(node, "identifier"))
    )


def parse_quantifier(prop: Tree) -> QuantifierExprNode:
    q = find_node(prop, "quantifier_expr")

    return QuantifierExprNode(
        quantifier=node_value(q),
        domain=parse_domain(prop),
    )