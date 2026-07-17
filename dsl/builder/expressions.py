from __future__ import annotations

from lark import Tree

from dsl.ast.nodes.expressions import (
    AtExprNode,
    CheckAtExprNode,
    PairwiseExprNode,
    QuantifierBinderNode,
    QuantifierExprNode,
)
from dsl.builder.core.ast_utils import node_value
from dsl.builder.core.source import with_source_span
from dsl.builder.core.strict import optional, require_node, require_value
from dsl.builder.core.utils import find_child, find_node, get_node_name_or_value
from dsl.builder.domain import parse_domain
from dsl.builder.neighborhood import parse_local_neighborhood, parse_neighborhood
from dsl.builder.restrictions import parse_restriction


def _direct_trees(node: Tree, data: str) -> list[Tree]:
    return [
        child
        for child in node.children
        if isinstance(child, Tree) and child.data == data
    ]


def _identifier_values(node: Tree) -> list[str]:
    values: list[str] = []
    for identifier in _direct_trees(node, "identifier"):
        values.append(
            require_value(node_value(identifier), "Identifier is missing or invalid")
        )
    return values


def parse_at(prop: Tree) -> AtExprNode:
    node = require_node(find_node(prop, "at_expr"), "at_expr node not found")
    identifiers = _direct_trees(node, "identifier")
    if len(identifiers) != 1:
        raise ValueError("at expression requires exactly one direct anchor identifier")

    variable = require_value(
        node_value(identifiers[0]), "Identifier value cannot be None"
    )
    local = find_node(node, "local_neighborhood")

    if local is not None:
        result = AtExprNode(
            variable=variable,
            neighborhood=None,
            domain=None,
            local_membership=parse_local_neighborhood(local, anchor=variable),
        )
    else:
        result = AtExprNode(
            variable=variable,
            neighborhood=optional(node, "neighborhood", parse_neighborhood),
            domain=optional(node, "domain", parse_domain),
        )

    return with_source_span(result, node)


def parse_pairwise_token(pair: str) -> tuple[str, str]:
    """Parse the retained legacy pairwise token ``x ~ x'``."""
    parts = [part.strip() for part in pair.split("~")]
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
    node = require_node(
        find_node(prop, "pairwise_expr"), "pairwise_expr node not found"
    )
    pair_node = require_node(
        find_child(node, "pairwise_token"), "pairwise_token node not found"
    )
    pair = require_value(node_value(pair_node), "pairwise_token is missing or invalid")
    left, right = parse_pairwise_token(pair)

    result = PairwiseExprNode(
        left=left,
        right=right,
        neighborhood=parse_neighborhood(node),
        domain=optional(node, "domain", parse_domain),
    )
    return with_source_span(result, node)


def parse_check_at(prop: Tree) -> CheckAtExprNode:
    node = require_node(find_node(prop, "check_expr"), "check_expr node not found")
    identifier = require_node(
        find_child(node, "identifier"), "check_at identifier not found"
    )
    result = CheckAtExprNode(
        variable=require_value(
            node_value(identifier), "check_at identifier is missing or invalid"
        )
    )
    return with_source_span(result, node)


def _parse_binder(node: Tree) -> QuantifierBinderNode:
    quantifier_node = require_node(
        find_child(node, "quantifier"), "quantifier node not found"
    )
    quantifier = require_value(
        get_node_name_or_value(quantifier_node), "quantifier is missing or invalid"
    )
    variables = _identifier_values(node)
    if not variables:
        raise ValueError("Quantifier binder requires at least one identifier")

    binder = QuantifierBinderNode(quantifier=quantifier, variables=variables)
    return with_source_span(binder, node)


def parse_quantifier(prop: Tree) -> QuantifierExprNode:
    node = require_node(
        find_node(prop, "quantifier_expr"), "quantifier_expr node not found"
    )

    first_quantifier = require_node(
        find_child(node, "quantifier"), "initial quantifier node not found"
    )
    first_variables = _identifier_values(node)
    first_binder = QuantifierBinderNode(
        quantifier=require_value(
            get_node_name_or_value(first_quantifier),
            "initial quantifier is missing or invalid",
        ),
        variables=first_variables,
    )
    with_source_span(first_binder, node)

    binders = [first_binder]
    binders.extend(
        _parse_binder(clause) for clause in _direct_trees(node, "quantifier_clause")
    )

    domain = optional(node, "domain", parse_domain)
    where_clause = find_child(node, "where_clause")
    restriction = parse_restriction(where_clause) if where_clause is not None else None

    result = QuantifierExprNode(
        binders=binders,
        domain=domain,
        restriction=restriction,
    )
    return with_source_span(result, node)
