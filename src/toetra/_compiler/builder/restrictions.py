from __future__ import annotations

from lark import Tree

from toetra._compiler.ast.nodes.expressions import RestrictionNode
from toetra._compiler.builder.assertion import parse_assertion
from toetra._compiler.builder.core.source import with_source_span
from toetra._compiler.builder.core.strict import require_node
from toetra._compiler.builder.core.utils import find_child
from toetra._compiler.builder.neighborhood import parse_neighborhood_membership


def parse_restriction(where_clause: Tree) -> RestrictionNode:
    """Build one source restriction without lowering quantifier semantics."""
    restriction = require_node(
        find_child(where_clause, "restriction"), "where restriction not found"
    )
    membership = find_child(restriction, "neighborhood_membership")

    if membership is not None:
        expression = parse_neighborhood_membership(membership)
    else:
        logical_children = [
            child for child in restriction.children if isinstance(child, Tree)
        ]
        if len(logical_children) != 1:
            raise ValueError("Restriction must contain exactly one expression")
        expression = parse_assertion(logical_children[0])

    return with_source_span(RestrictionNode(expression=expression), where_clause)
