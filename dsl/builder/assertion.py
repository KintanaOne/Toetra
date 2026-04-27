from typing import List, Union

from lark import Tree, Token

from dsl.ast.nodes.assertion import (
    AndNode,
    AssertionNode,
    ComparisonNode,
    ImplicationNode,
    OrNode,
    NotNode,
    ProblemNode,
    UnknownNode,
    LogicalNode,
)

from dsl.builder.core.utils import find_node, get_token_value
from dsl.builder.core.ast_utils import parse_attribute, node_value, parse_value
from dsl.language.vocabulary.logic_operations import EnumLogicOperation


# ============================================================================  
# COMPARISON  
# ============================================================================  

def build_logic_expr(node: Tree) -> LogicalNode:
    attribute_node = find_node(node, "attribute")
    value_node = find_node(node, "value")
    op_node = find_node(node, "logic_operation")

    if attribute_node is None or value_node is None or op_node is None:
        raise ValueError("Invalid comparison")

    left = parse_attribute(attribute_node)
    op = EnumLogicOperation(get_token_value(op_node))
    right = parse_value(value_node)

    return ComparisonNode(left=left, op=op, right=right)

# ============================================================================  
# UTILS  
# ============================================================================  

def _extract_trees(node: Tree) -> List[Tree]:
    return [c for c in node.children if isinstance(c, Tree)]


# ============================================================================  
# CORE PARSER  
# ============================================================================  

def parse_assertion(node: Tree | Token | None) -> LogicalNode:

    if node is None:
        raise ValueError("Assertion node is None")

    if isinstance(node, Token):
        raise ValueError(f"Unexpected token: {node.value}")

    t = node.data
    children = _extract_trees(node)

    # ----------------------------------------------------------------------
    # IMPLY
    # ----------------------------------------------------------------------
    if t == "logical_imply":
        if len(children) != 2:
            raise ValueError("Invalid implication")

        return ImplicationNode(
            left=parse_assertion(children[0]),
            right=parse_assertion(children[1]),
        )

    # ----------------------------------------------------------------------
    # OR
    # ----------------------------------------------------------------------
    if t == "logic_or":
        return OrNode(
            operands=[parse_assertion(c) for c in children]
        )

    # ----------------------------------------------------------------------
    # AND
    # ----------------------------------------------------------------------
    if t == "logic_and":
        return AndNode(
            operands=[parse_assertion(c) for c in children]
        )

    # ----------------------------------------------------------------------
    # NOT
    # ----------------------------------------------------------------------
    if t == "logic_not":
        if not children:
            raise ValueError("NOT requires an operand")

        return NotNode(
            operand=parse_assertion(children[-1])
        )

    # ----------------------------------------------------------------------
    # COMPARISON
    # ----------------------------------------------------------------------
    if t == "logic_expr":
        return build_logic_expr(node)

    # ----------------------------------------------------------------------
    # ATOM
    # ----------------------------------------------------------------------
    if t == "atom":
        if not children:
            raise ValueError("Empty atom")
        return parse_assertion(children[0])

    # ----------------------------------------------------------------------
    # PROBLEM (IMPORTANT)
    # ----------------------------------------------------------------------
    if t == "problem_expr":
        problem = "UNKNOWN"
        function = None

        for c in node.children:
            if isinstance(c, Token):
                problem = c.value
            elif isinstance(c, Tree):
                function = node_value(c)

        return ProblemNode(problem=problem, function=function)

    # ----------------------------------------------------------------------
    # FALLBACK
    # ----------------------------------------------------------------------
    raise ValueError(f"Unhandled node: {t}")
