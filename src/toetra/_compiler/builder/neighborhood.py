from __future__ import annotations

from lark import Token, Tree

from toetra._compiler.ast.nodes.neighborhood import (
    NeighborhoodMembershipNode,
    NeighborhoodNode,
)
from toetra._compiler.ast.nodes.primitives import ArgNode
from toetra._compiler.builder.core.ast_utils import (
    clean_string,
    node_value,
    parse_value,
)
from toetra._compiler.builder.core.source import with_source_span
from toetra._compiler.builder.core.strict import require_node, require_value
from toetra._compiler.builder.core.utils import find_all_nodes, find_child, find_node
from toetra._compiler.builder.scalar import parse_scalar_expression


def _parse_arg(arg_node: Tree) -> ArgNode:
    eq = find_child(arg_node, "arg_identifier_eq")
    if eq is None:
        raise ValueError("Neighborhood arguments must use the explicit name=value form")

    key_node = find_child(eq, "quoted_identifier")
    value_node = find_child(eq, "value")
    key = clean_string(node_value(key_node))

    if not key:
        raise ValueError("Missing neighborhood argument key")
    if value_node is None:
        raise ValueError(f"Missing neighborhood argument value for key={key}")

    argument = ArgNode(key=key, value=parse_value(value_node).value)
    return with_source_span(argument, arg_node)


def _parse_args(args_node: Tree | None) -> list[ArgNode]:
    if args_node is None:
        return []

    arguments: list[ArgNode] = []
    names: set[str] = set()
    for arg_node in find_all_nodes(args_node, "arg"):
        argument = _parse_arg(arg_node)
        if argument.key in names:
            raise ValueError(f"Duplicate neighborhood argument '{argument.key}'")
        names.add(argument.key)
        arguments.append(argument)
    return arguments


def _extract_metric(node: Tree) -> str:
    metric_tokens = {"L1", "L2", "LINF"}
    for child in node.scan_values(lambda value: isinstance(value, Token)):
        if child.type in metric_tokens:
            return child.value
    raise ValueError("No metric token found in neighborhood")


def parse_neighborhood(node: Tree) -> NeighborhoodNode:
    """Parse the retained legacy ``in neighborhood(metric, args...)`` form."""
    neighborhood = require_node(
        find_node(node, "neighborhood"), "Neighborhood node not found"
    )
    result = NeighborhoodNode(
        metric=_extract_metric(neighborhood),
        args=_parse_args(find_child(neighborhood, "args")),
    )
    return with_source_span(result, neighborhood)


def _identifier_from_argument(node: Tree, label: str) -> str:
    identifier = require_node(find_child(node, "identifier"), f"Missing {label}")
    return require_value(node_value(identifier), f"Invalid {label}")


def parse_neighborhood_membership(node: Tree) -> NeighborhoodMembershipNode:
    """Parse natural ``x in neighborhood(of = a, metric = ..., eps = ...)``."""
    candidate_node = require_node(
        find_child(node, "identifier"), "Neighborhood candidate missing"
    )
    of_argument = require_node(
        find_child(node, "neighborhood_of_argument"), "Neighborhood anchor missing"
    )
    metric_argument = require_node(
        find_child(node, "neighborhood_metric_argument"),
        "Neighborhood metric missing",
    )
    eps_argument = require_node(
        find_child(node, "neighborhood_eps_argument"), "Neighborhood epsilon missing"
    )
    scalar = require_node(
        find_child(eps_argument, "scalar_expression"),
        "Neighborhood epsilon expression missing",
    )

    membership = NeighborhoodMembershipNode(
        candidate=require_value(
            node_value(candidate_node), "Neighborhood candidate is invalid"
        ),
        anchor=_identifier_from_argument(of_argument, "neighborhood anchor"),
        metric=_extract_metric(metric_argument),
        epsilon=parse_scalar_expression(scalar),
    )
    return with_source_span(membership, node)


def parse_local_neighborhood(
    node: Tree,
    *,
    anchor: str,
) -> NeighborhoodMembershipNode:
    """Parse ``with candidate in neighborhood(metric=..., eps=...)`` sugar."""
    candidate_node = require_node(
        find_child(node, "identifier"), "Local neighborhood candidate missing"
    )
    metric_argument = require_node(
        find_child(node, "neighborhood_metric_argument"),
        "Local neighborhood metric missing",
    )
    eps_argument = require_node(
        find_child(node, "neighborhood_eps_argument"),
        "Local neighborhood epsilon missing",
    )
    scalar = require_node(
        find_child(eps_argument, "scalar_expression"),
        "Local neighborhood epsilon expression missing",
    )

    membership = NeighborhoodMembershipNode(
        candidate=require_value(
            node_value(candidate_node), "Local neighborhood candidate is invalid"
        ),
        anchor=anchor,
        metric=_extract_metric(metric_argument),
        epsilon=parse_scalar_expression(scalar),
    )
    return with_source_span(membership, node)
