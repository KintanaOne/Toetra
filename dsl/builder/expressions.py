from lark import Tree
from dsl.ast.nodes.expressions import (
    AtExprNode, 
    CheckAtExprNode, 
    PairwiseExprNode,
    QuantifierExprNode
)
from dsl.builder.core.strict import optional, require_value, safe_find_child, safe_find_node
from dsl.builder.core.utils import find_child, find_node, get_node_name_or_value
from dsl.builder.core.ast_utils import node_value
from dsl.builder.domain import parse_domain
from dsl.builder.neighborhood import parse_neighborhood

from dsl.builder.core.strict import require_node

# ============================================================================
# EXPRESSIONS (AT / CHECK / PAIRWISE / QUANTIFIER)
# ============================================================================

def parse_at(prop: Tree) -> AtExprNode:
    # =========================================================================
    # AT EXPRESSION PARSING
    # =========================================================================
    # This function converts a Lark parse tree into a strict AtExprNode.
    # All structural validations are enforced through safe helpers.
    # =========================================================================

    node = safe_find_node(prop, "at_expr")

    identifier_node = safe_find_child(node, "identifier")

    variable = require_value(
        node_value(identifier_node),
        "Identifier value cannot be None"
    )

    neighborhood = optional(node, "neighborhood", parse_neighborhood)
    domain = optional(node, "domain", parse_domain)

    return AtExprNode(
        variable=variable,
        neighborhood=neighborhood,
        domain=domain,
    )





# ============================================================================
# EXPRESSIONS PARSERS (STRICT VERSION)
# ============================================================================


def parse_pairwise(prop: Tree) -> PairwiseExprNode:
    """
    Parse a pairwise expression into a strict AST node.
    """

    # --- 1. Ensure pairwise_expr exists ---
    node = require_node(
        find_node(prop, "pairwise_expr"),
        "pairwise_expr node not found"
    )

    # --- 2. Extract pair token (mandatory) ---
    pair_node = require_node(
        find_child(node, "pairwise_token"),
        "pairwise_token node not found"
    )

    pair = require_value(
        node_value(pair_node),
        "pairwise_token is missing or invalid"
    )

    # --- 3. Neighborhood (depends on your grammar: required here) ---
    neighborhood = parse_neighborhood(node)

    # --- 4. Domain (OPTIONAL) ---
    domain = optional(node, "domain", parse_domain)

    # --- 5. Build AST ---
    return PairwiseExprNode(
        pair=pair,
        neighborhood=neighborhood,
        domain=domain
    )

# ---------------------------------------------------------------------------

def parse_check_at(prop: Tree) -> CheckAtExprNode:
    """
    Parse a check_at expression into a strict AST node.
    """

    node = require_node(
        find_node(prop, "check_expr"),
        "check_expr node not found"
    )

    identifier_node = find_child(node, "identifier")

    variable = require_value(
        node_value(identifier_node),
        "identifier is missing or invalid"
    )

    return CheckAtExprNode(variable=variable)


# ---------------------------------------------------------------------------

def parse_quantifier(prop: Tree) -> QuantifierExprNode:

    node = require_node(
        find_node(prop, "quantifier_expr"),
        "quantifier_expr node not found"
    )

    quantifier_node = require_node(
        find_child(node, "quantifier"),
        "quantifier node not found"
    )

    quantifier_child = require_node(
        quantifier_node.children[0] if quantifier_node.children else None,
        "quantifier value missing"
        )

    quantifier = get_node_name_or_value(quantifier_node)
    
    quantifier = require_value(
        quantifier,
        "quantifier is missing or invalid"
    )

    domain = optional(node, "domain", parse_domain)

    return QuantifierExprNode(
        quantifier=quantifier,
        domain=domain,
    )