from __future__ import annotations

from typing import Any

from lark import Token, Tree

from dsl.ast.nodes.neighborhood import NeighborhoodMembershipNode, NeighborhoodNode
from dsl.ast.nodes.primitives import ArgNode
from dsl.builder.core.ast_utils import clean_string, node_value
from dsl.builder.core.source import with_source_span
from dsl.builder.core.strict import require_node, require_value
from dsl.builder.core.utils import find_all_nodes, find_child, find_node
from dsl.builder.scalar import parse_scalar_expression
from dsl.parser.errors import ParserPropertyError


def _parse_numeric(value: Any) -> Any:
    """Convert a legacy argument spelling to int/float when possible."""
    try:
        return int(value)
    except (TypeError, ValueError):
        pass

    try:
        return float(value)
    except (TypeError, ValueError):
        return value


def _parse_arg(arg_node: Tree) -> ArgNode:
    eq = find_child(arg_node, "arg_identifier_eq")
    if eq is None:
        raise ParserPropertyError("Missing '=' in argument")

    key_node = find_child(eq, "quoted_identifier")
    val_node = find_child(eq, "value")

    if val_node is None:
        raise ParserPropertyError("Missing argument value in neighborhood argument")

    key = require_value(node_value(key_node), "Missing argument key")
    raw_val = node_value(val_node)
    if raw_val is None:
        raise ParserPropertyError(f"Missing argument value for key={key}")

    try:
        val = _parse_numeric(raw_val)
    except Exception:
        val = clean_string(raw_val)

    return ArgNode(key=key, value=val)


def _parse_args(args_node: Tree | None) -> list[ArgNode]:
    if args_node is None:
        return []
    return [_parse_arg(arg) for arg in find_all_nodes(args_node, "arg")]


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
