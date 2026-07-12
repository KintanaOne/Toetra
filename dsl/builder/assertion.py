from typing import List

from lark import Tree, Token

from dsl.ast.nodes.assertion import (
    AndNode,
    ComparisonNode,
    ImplicationNode,
    OrNode,
    NotNode,
    ProblemNode,
    LogicalNode,
)

from dsl.builder.core.utils import get_token_value
from dsl.builder.core.ast_utils import node_value
from dsl.language.vocabulary.functions import EnumFunction
from dsl.language.vocabulary.operators import EnumComparisonOperator
from dsl.language.vocabulary.problems import EnumProblem
from dsl.builder.scalar import parse_scalar_expression

# ============================================================================
# COMPARISON
# ============================================================================


def build_comparison_expr(node: Tree) -> ComparisonNode:
    scalar_nodes = [
        child
        for child in node.children
        if isinstance(child, Tree) and str(child.data) == "scalar_expression"
    ]
    op_node = next(
        (
            child
            for child in node.children
            if isinstance(child, Tree) and str(child.data) == "comparison_operation"
        ),
        None,
    )

    if len(scalar_nodes) != 2 or op_node is None:
        raise ValueError("Invalid comparison")

    left = parse_scalar_expression(scalar_nodes[0])
    right = parse_scalar_expression(scalar_nodes[1])
    op = EnumComparisonOperator(get_token_value(op_node))

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
        return OrNode(operands=[parse_assertion(c) for c in children])

    # ----------------------------------------------------------------------
    # AND
    # ----------------------------------------------------------------------
    if t == "logic_and":
        return AndNode(operands=[parse_assertion(c) for c in children])

    # ----------------------------------------------------------------------
    # NOT
    # ----------------------------------------------------------------------
    if t == "logic_not":
        if not children:
            raise ValueError("NOT requires an operand")

        return NotNode(operand=parse_assertion(children[-1]))

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
