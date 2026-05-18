from lark import Tree

from dsl.builder.core.utils import find_all_nodes
from dsl.builder.header import parse_model, parse_target
from dsl.builder.property import parse_property

from dsl.ast.nodes.program import ProgramNode
from dsl.ast.nodes.header import HeaderNode

# ============================================================================
# PROGRAM ENTRYPOINT
# ============================================================================


def parse_program(tree: Tree) -> ProgramNode:
    # ------------------------------------------------------------------------
    # HEADER
    # ------------------------------------------------------------------------
    model = parse_model(tree)
    target = parse_target(tree)

    header = HeaderNode(model=model, target=target)

    # ------------------------------------------------------------------------
    # BODY
    # ------------------------------------------------------------------------
    properties = [parse_property(p) for p in find_all_nodes(tree, "property_section")]

    # ------------------------------------------------------------------------
    # PROGRAM NODE
    # ------------------------------------------------------------------------
    return ProgramNode(header=header, body=properties)
