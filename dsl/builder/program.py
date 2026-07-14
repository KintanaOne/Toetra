from lark import Tree

from dsl.builder.core.utils import find_all_nodes
from dsl.builder.header import parse_header
from dsl.builder.property import parse_property

from dsl.ast.nodes.program import ProgramNode

# ============================================================================
# PROGRAM ENTRYPOINT
# ============================================================================


def parse_program(tree: Tree) -> ProgramNode:
    # ------------------------------------------------------------------------
    # HEADER
    # ------------------------------------------------------------------------
    header = parse_header(tree)

    # ------------------------------------------------------------------------
    # BODY
    # ------------------------------------------------------------------------
    properties = [parse_property(p) for p in find_all_nodes(tree, "property_section")]

    # ------------------------------------------------------------------------
    # PROGRAM NODE
    # ------------------------------------------------------------------------
    return ProgramNode(header=header, body=properties)
