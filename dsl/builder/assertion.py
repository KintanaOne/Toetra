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
from dsl.language.vocabulary.functions import EnumFunction
from dsl.language.vocabulary.operators import EnumComparisonOperator
from dsl.language.vocabulary.problems import EnumProblem


# ============================================================================  
# COMPARISON  
# ============================================================================  

def build_comparison_expr(node: Tree) -> ComparisonNode:
    attribute_node = find_node(node, "attribute")
    value_node = find_node(node, "value")
    op_node = find_node(node, "comparison_operation")

    if attribute_node is None or value_node is None or op_node is None:
        raise ValueError("Invalid comparison")

    left = parse_attribute(attribute_node)
    op = EnumComparisonOperator(get_token_value(op_node))
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
        
    if t == "comparison_expr":
        return build_comparison_expr(node)

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
        problem: EnumProblem | None = None
        function: EnumFunction | None = None

        for c in node.children:
            if isinstance(c, Token):
                try:
                    problem = EnumProblem(c.value)
                except ValueError:
                    raise ValueError(f"Unknown problem: {c.value}")

            elif isinstance(c, Tree):
                try:
                    function = EnumFunction(node_value(c))
                except ValueError:
                    raise ValueError(f"Unknown function: {node_value(c)}")
                
        if problem is None:
            raise ValueError("Missing problem")

        return ProblemNode(problem=problem, function=function)

    # ----------------------------------------------------------------------
    # FALLBACK
    # ----------------------------------------------------------------------
    raise ValueError(f"Unhandled node: {t}")
