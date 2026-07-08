from lark import Tree
from dsl.ast.nodes.expressions import (
    AtExprNode,
    CheckAtExprNode,
    PairwiseExprNode,
    QuantifierExprNode,
)
from dsl.builder.core.strict import (
    optional,
    require_value,
    safe_find_child,
    safe_find_node,
)
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
        node_value(identifier_node), "Identifier value cannot be None"
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


def parse_pairwise_token(pair: str) -> tuple[str, str]:
    """
    Parse a raw pairwise token like:
        x ~ x'

    Returns:
        (left, right)
    """

    parts = [p.strip() for p in pair.split("~")]

    if len(parts) != 2:
        raise ValueError(f"Invalid pairwise token '{pair}', expected 'x ~ x\\''")

    left, right = parts

    if not left or not right:
        raise ValueError("Pairwise expression requires two variables")

    if not right.endswith("'"):
        raise ValueError(
            f"Right variable '{right}' must be a primed version of '{left}'"
        )

    if right[:-1] != left:
        raise ValueError(
            f"Invalid pairwise token '{pair}', expected '{left} ~ {left}\\''"
        )

    return left, right


def parse_pairwise(prop: Tree) -> PairwiseExprNode:
    """
    Parse a pairwise expression into a strict AST node.
    """

    # --- 1. Ensure pairwise_expr exists ---
    node = require_node(
        find_node(prop, "pairwise_expr"), "pairwise_expr node not found"
    )

    # --- 2. Extract pair token (mandatory) ---
    pair_node = require_node(
        find_child(node, "pairwise_token"), "pairwise_token node not found"
    )

    pair = require_value(node_value(pair_node), "pairwise_token is missing or invalid")

    left, right = parse_pairwise_token(pair)

    # --- 3. Neighborhood ---
    neighborhood = parse_neighborhood(node)

    # --- 4. Domain (OPTIONAL) ---
    domain = optional(node, "domain", parse_domain)

    # --- 5. Build AST ---
    return PairwiseExprNode(
        left=left,
        right=right,
        neighborhood=neighborhood,
        domain=domain,
    )


# ---------------------------------------------------------------------------


def parse_check_at(prop: Tree) -> CheckAtExprNode:
    """
    Parse a check_at expression into a strict AST node.
    """

    node = require_node(find_node(prop, "check_expr"), "check_expr node not found")

    identifier_node = find_child(node, "identifier")

    variable = require_value(
        node_value(identifier_node), "identifier is missing or invalid"
    )

    return CheckAtExprNode(variable=variable)


# ---------------------------------------------------------------------------


def parse_quantifier(prop: Tree) -> QuantifierExprNode:

    node = require_node(
        find_node(prop, "quantifier_expr"), "quantifier_expr node not found"
    )

    quantifier_node = require_node(
        find_child(node, "quantifier"), "quantifier node not found"
    )

    quantifier = get_node_name_or_value(quantifier_node)

    quantifier = require_value(quantifier, "quantifier is missing or invalid")

    domain = optional(node, "domain", parse_domain)

    return QuantifierExprNode(
        quantifier=quantifier,
        domain=domain,
    )
