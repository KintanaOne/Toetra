from __future__ import annotations

from lark import Tree

from dsl.ast.nodes.assertion import AssertionNode
from dsl.ast.nodes.expressions import DirectExprNode
from dsl.ast.nodes.property import PropertyNode, PropertyRuleNode
from dsl.builder.assertion import parse_assertion
from dsl.builder.backends import parse_backend
from dsl.builder.core.ast_utils import node_value
from dsl.builder.core.source import with_source_span
from dsl.builder.core.strict import require_node, require_value
from dsl.builder.core.utils import find_child, find_node
from dsl.builder.expressions import (
    parse_at,
    parse_check_at,
    parse_pairwise,
    parse_quantifier,
)
from dsl.language.vocabulary.properties import EnumProperty


def _property_tree(section: Tree) -> Tree:
    if section.data == "property":
        return section
    return require_node(find_child(section, "property"), "property node not found")


def detect_mode(prop: Tree) -> str:
    """Detect the source property body without inspecting the assertion."""
    property_node = _property_tree(prop)
    expression = find_child(property_node, "property_expr")
    if expression is None:
        return "direct"
    if find_child(expression, "quantifier_expr") is not None:
        return "quantifier"
    if find_child(expression, "at_expr") is not None:
        return "at"
    if find_child(expression, "check_expr") is not None:
        return "check_at"
    if find_child(expression, "pairwise_expr") is not None:
        return "pairwise"
    raise ValueError("Unknown property expression")


def extract_scoped_rhs(prop: Tree) -> Tree:
    """Extract the assertion following the source-level ``=>`` separator."""
    found_imply = False
    for child in _property_tree(prop).children:
        if not isinstance(child, Tree):
            continue
        if child.data == "padding":
            continue
        if child.data in {"property_type", "property_expr"}:
            continue
        if child.data == "property_imply":
            found_imply = True
            continue
        if child.data == "backend":
            continue
        if found_imply:
            return child
    raise ValueError("Missing RHS in scoped property")


def extract_direct_assertion(prop: Tree) -> Tree:
    """Extract the assertion from a property with no source scope."""
    for child in _property_tree(prop).children:
        if not isinstance(child, Tree):
            continue
        if child.data in {"padding", "property_type", "backend"}:
            continue
        if child.data in {"property_expr", "property_imply"}:
            raise ValueError("Direct property unexpectedly contains a scope separator")
        return child
    raise ValueError("Missing assertion in direct property")


def parse_property(prop: Tree) -> PropertyNode:
    mode = detect_mode(prop)
    expression_parsers = {
        "at": parse_at,
        "pairwise": parse_pairwise,
        "check_at": parse_check_at,
        "quantifier": parse_quantifier,
    }

    if mode == "direct":
        right_node = extract_direct_assertion(prop)
        left = with_source_span(DirectExprNode(), right_node)
    else:
        left = expression_parsers[mode](prop)
        right_node = extract_scoped_rhs(prop)

    assertion = AssertionNode(root=parse_assertion(right_node))
    with_source_span(assertion, right_node)

    property_type_node = require_node(
        find_node(prop, "property_type"), "Property type is missing"
    )
    property_type = EnumProperty(
        require_value(node_value(property_type_node), "Property type is missing")
    )

    property_node = PropertyNode(
        type=property_type,
        rule=PropertyRuleNode(scope=left, assertion=assertion),
        backend=parse_backend(find_node(prop, "backend")),
    )
    return with_source_span(property_node, _property_tree(prop))
