from lark import Tree
from dsl.builder.core.strict import require_node, require_value
from dsl.builder.core.utils import find_child, find_all_nodes, find_node
from dsl.builder.core.ast_utils import node_value, clean_string
from dsl.ast.nodes.domain import DomainNode


# ============================================================================
# DOMAIN PARSER
# ============================================================================
# This parser builds a strict DomainNode from a Lark tree.
# All missing or invalid nodes are rejected immediately to enforce AST integrity.
# ============================================================================


def parse_domain(node: Tree) -> DomainNode:
    # ------------------------------------------------------------------------
    # Retrieve domain node (must exist)
    # ------------------------------------------------------------------------
    domain = require_node(
        find_node(node, "domain"),
        "Domain node not found"
    )

    # ------------------------------------------------------------------------
    # Extract domain identifier (must exist and be valid string)
    # ------------------------------------------------------------------------
    identifier_node = find_child(domain, "identifier")

    name = require_value(
        node_value(identifier_node),
        "Missing domain name"
    )

    # ------------------------------------------------------------------------
    # Extract and sanitize domain values
    # ------------------------------------------------------------------------
    values = [
        require_value(
            clean_string(node_value(v)),
            "Invalid domain value"
        )
        for v in find_all_nodes(domain, "value")
    ]

    # ------------------------------------------------------------------------
    # Build AST node
    # ------------------------------------------------------------------------
    return DomainNode(
        name=name,
        values=values,
    )