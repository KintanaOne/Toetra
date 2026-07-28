from lark import Tree

from toetra._compiler.builder.anchors import parse_anchor_declaration
from toetra._compiler.builder.core.utils import find_all_nodes
from toetra._compiler.builder.errors import BuilderError
from toetra._compiler.builder.header import parse_header
from toetra._compiler.builder.property import parse_property

from toetra._compiler.ast.nodes.program import ProgramNode

# ============================================================================
# PROGRAM ENTRYPOINT
# ============================================================================


def parse_program(tree: Tree) -> ProgramNode:
    try:
        return _parse_program(tree)
    except BuilderError:
        raise
    except (AttributeError, IndexError, KeyError, TypeError, ValueError) as error:
        raise BuilderError(
            str(error) or "The parsed source cannot be represented as a Toetra AST.",
            hint="Check that every declaration and property is structurally complete.",
        ) from error


def _parse_program(tree: Tree) -> ProgramNode:
    # ------------------------------------------------------------------------
    # HEADER
    # ------------------------------------------------------------------------
    header = parse_header(tree)

    # ------------------------------------------------------------------------
    # GLOBAL ANCHORS
    # ------------------------------------------------------------------------
    anchors = [
        parse_anchor_declaration(anchor)
        for anchor in find_all_nodes(tree, "anchor_declaration")
    ]

    # ------------------------------------------------------------------------
    # BODY
    # ------------------------------------------------------------------------
    properties = [parse_property(p) for p in find_all_nodes(tree, "property_section")]

    # ------------------------------------------------------------------------
    # PROGRAM NODE
    # ------------------------------------------------------------------------
    return ProgramNode(header=header, body=properties, anchors=anchors)
