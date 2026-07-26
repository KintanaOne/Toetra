from __future__ import annotations

from lark import Token, Tree

from toetra._compiler.ast.nodes.anchors import (
    AnchorDeclarationNode,
    AnchorEntryNode,
    AnchorReferenceArgumentNode,
    AnchorReferenceBindingNode,
    InlineAnchorBindingNode,
)
from toetra._compiler.builder.core.ast_utils import (
    node_value,
    parse_literal_value,
    parse_value,
)
from toetra._compiler.builder.core.source import with_source_span
from toetra._compiler.builder.core.strict import require_node, require_value
from toetra._compiler.builder.core.utils import find_all_nodes, find_child


def _literal_text(node: Tree) -> str:
    tokens = [
        str(token) for token in node.scan_values(lambda value: isinstance(value, Token))
    ]
    if not tokens:
        raise ValueError("Anchor literal has no value")
    return "".join(tokens)


def _parse_anchor_entry(node: Tree) -> AnchorEntryNode:
    identifier = require_node(find_child(node, "identifier"), "Anchor feature missing")
    literal = require_node(find_child(node, "anchor_literal"), "Anchor literal missing")
    entry = AnchorEntryNode(
        feature=require_value(node_value(identifier), "Anchor feature is invalid"),
        value=parse_literal_value(_literal_text(literal)),
    )
    return with_source_span(entry, node)


def _parse_inline_anchor(node: Tree) -> InlineAnchorBindingNode:
    binding = InlineAnchorBindingNode(
        entries=[
            _parse_anchor_entry(entry) for entry in find_all_nodes(node, "anchor_entry")
        ]
    )
    return with_source_span(binding, node)


def _parse_reference_argument(node: Tree) -> AnchorReferenceArgumentNode:
    argument_children = [child for child in node.children if isinstance(child, Tree)]
    if len(argument_children) != 1:
        raise ValueError(
            "Anchor reference argument must wrap exactly one named argument"
        )

    named = argument_children[0]
    if named.data == "anchor_ref_key_argument":
        name = "key"
    elif named.data == "anchor_ref_value_argument":
        name = "value"
    else:
        raise ValueError(f"Unsupported anchor reference argument: {named.data}")

    value_node = require_node(find_child(named, "value"), f"Missing ref {name} value")
    argument = AnchorReferenceArgumentNode(name=name, value=parse_value(value_node))
    return with_source_span(argument, node)


def _parse_anchor_reference(node: Tree) -> AnchorReferenceBindingNode:
    binding = AnchorReferenceBindingNode(
        arguments=[
            _parse_reference_argument(argument)
            for argument in find_all_nodes(node, "anchor_ref_argument")
        ]
    )
    return with_source_span(binding, node)


def parse_anchor_declaration(node: Tree) -> AnchorDeclarationNode:
    identifier = require_node(find_child(node, "identifier"), "Anchor name missing")
    binding_node = require_node(
        find_child(node, "anchor_binding"), "Anchor binding missing"
    )

    inline = find_child(binding_node, "inline_anchor")
    reference = find_child(binding_node, "anchor_ref")

    if inline is not None:
        binding = _parse_inline_anchor(inline)
    elif reference is not None:
        binding = _parse_anchor_reference(reference)
    else:
        raise ValueError("Unsupported anchor binding")

    declaration = AnchorDeclarationNode(
        name=require_value(node_value(identifier), "Anchor name is invalid"),
        binding=binding,
    )
    return with_source_span(declaration, node)
