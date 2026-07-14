from __future__ import annotations

from lark import Tree

from dsl.ast.nodes.domain import (
    DomainConstraintNode,
    DomainFiniteValueNode,
    DomainEntryNode,
    DomainNode,
    FiniteSetDomainNode,
    IntervalDomainNode,
)
from dsl.ast.nodes.primitives import NameRefNode
from dsl.builder.core.ast_utils import node_value, parse_attribute, parse_value
from dsl.builder.core.strict import require_node, require_value
from dsl.builder.core.utils import find_child, find_node
from dsl.builder.scalar import parse_scalar_expression
from dsl.language.vocabulary.domains import EnumBoundaryKind

_INTERVAL_BOUNDARIES: dict[
    str,
    tuple[EnumBoundaryKind, EnumBoundaryKind],
] = {
    "closed_closed_interval": (
        EnumBoundaryKind.CLOSED,
        EnumBoundaryKind.CLOSED,
    ),
    "open_closed_interval": (
        EnumBoundaryKind.OPEN,
        EnumBoundaryKind.CLOSED,
    ),
    "closed_open_interval": (
        EnumBoundaryKind.CLOSED,
        EnumBoundaryKind.OPEN,
    ),
    "open_open_interval": (
        EnumBoundaryKind.OPEN,
        EnumBoundaryKind.OPEN,
    ),
}


def _direct_children(node: Tree, rule: str) -> list[Tree]:
    return [
        child
        for child in node.children
        if isinstance(child, Tree) and str(child.data) == rule
    ]


def _parse_interval(node: Tree) -> IntervalDomainNode:
    concrete: Tree | None = None

    for rule in _INTERVAL_BOUNDARIES:
        concrete = find_child(node, rule)
        if concrete is not None:
            break

    if concrete is None:
        raise ValueError("Unsupported interval-domain shape")

    scalar_nodes = _direct_children(concrete, "scalar_expression")
    if len(scalar_nodes) != 2:
        raise ValueError("Interval domain requires exactly two bounds")

    lower_boundary, upper_boundary = _INTERVAL_BOUNDARIES[str(concrete.data)]

    return IntervalDomainNode(
        lower=parse_scalar_expression(scalar_nodes[0]),
        upper=parse_scalar_expression(scalar_nodes[1]),
        lower_boundary=lower_boundary,
        upper_boundary=upper_boundary,
    )


def _parse_finite_set_value(node: Tree) -> DomainFiniteValueNode:
    symbolic = find_child(node, "symbolic_literal")
    if symbolic is not None:
        identifier = require_node(
            find_child(symbolic, "identifier"),
            "Symbolic domain literal requires an identifier",
        )
        name = require_value(
            node_value(identifier),
            "Symbolic domain literal cannot be empty",
        )
        return NameRefNode(name=name)

    value = require_node(
        find_child(node, "value"),
        "Finite-set domain value is invalid",
    )
    return parse_value(value)


def _parse_finite_set(node: Tree) -> FiniteSetDomainNode:
    values: list[DomainFiniteValueNode] = [
        _parse_finite_set_value(value)
        for value in _direct_children(node, "finite_set_value")
    ]

    if not values:
        raise ValueError("Finite-set domain cannot be empty")

    return FiniteSetDomainNode(values=values)


def _parse_constraint(node: Tree) -> DomainConstraintNode:
    interval = find_child(node, "interval_domain")
    if interval is not None:
        return _parse_interval(interval)

    finite_set = find_child(node, "finite_set_domain")
    if finite_set is not None:
        return _parse_finite_set(finite_set)

    raise ValueError("Unsupported domain constraint")


def _parse_entry(node: Tree) -> DomainEntryNode:
    subject_node = require_node(
        find_child(node, "attribute"),
        "Domain entry requires an attribute subject",
    )
    constraint_node = require_node(
        find_child(node, "domain_constraint"),
        "Domain entry requires a constraint",
    )

    return DomainEntryNode(
        subject=parse_attribute(subject_node),
        constraint=_parse_constraint(constraint_node),
    )


def parse_domain(node: Tree) -> DomainNode:
    """Build a typed domain AST without performing semantic validation."""

    domain = require_node(find_node(node, "domain"), "Domain node not found")
    entries = [
        _parse_entry(entry) for entry in _direct_children(domain, "domain_entry")
    ]

    if not entries:
        raise ValueError("Domain requires at least one entry")

    return DomainNode(entries=entries)
