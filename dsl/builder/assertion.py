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


# ============================================================================  
# COMPARISON  
# ============================================================================  

def build_logic_expr(node: Tree) -> LogicalNode:
    attribute_node = find_node(node, "attribute")
    value_node = find_node(node, "value")
    op_node = find_node(node, "logic_operation")

    if attribute_node is None or value_node is None or op_node is None:
        return UnknownNode(raw="invalid_comparison")

    left = parse_attribute(attribute_node)
    op = str(get_token_value(op_node))
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

def parse_assertion(node: Union[Tree, Token, None]) -> AssertionNode:

    if node is None:
        return AssertionNode(root=UnknownNode(raw="None"))

    if isinstance(node, Token):
        return AssertionNode(root=UnknownNode(raw=node.value))

    t = node.data
    children = _extract_trees(node)

    # ----------------------------------------------------------------------
    # IMPLY
    # ----------------------------------------------------------------------
    if t == "logical_imply":
        if len(children) != 2:
            return AssertionNode(root=UnknownNode(raw="invalid_imply"))

        return AssertionNode(
            root=ImplicationNode(
                left=parse_assertion(children[0]).root,
                right=parse_assertion(children[1]).root,
            )
        )

    # ----------------------------------------------------------------------
    # OR
    # ----------------------------------------------------------------------
    if t == "logic_or":
        ops = [parse_assertion(c).root for c in children]

        if len(ops) == 1:
            return AssertionNode(root=ops[0])

        return AssertionNode(root=OrNode(operands=ops))

    # ----------------------------------------------------------------------
    # AND
    # ----------------------------------------------------------------------
    if t == "logic_and":
        ops = [parse_assertion(c).root for c in children]

        if len(ops) == 1:
            return AssertionNode(root=ops[0])

        return AssertionNode(root=AndNode(operands=ops))

    # ----------------------------------------------------------------------
    # NOT
    # ----------------------------------------------------------------------
    if t == "logic_not":
        if not children:
            return AssertionNode(root=UnknownNode(raw="empty_not"))

        return AssertionNode(
            root=NotNode(
                operand=parse_assertion(children[-1]).root
            )
        )

    # ----------------------------------------------------------------------
    # COMPARISON
    # ----------------------------------------------------------------------
    if t == "logic_expr":
        return AssertionNode(root=build_logic_expr(node))

    # ----------------------------------------------------------------------
    # ATOM
    # ----------------------------------------------------------------------
    if t == "atom":
        return parse_assertion(children[0]) if children else AssertionNode(root=UnknownNode(raw="empty_atom"))

    # ----------------------------------------------------------------------
    # PROBLEM
    # ----------------------------------------------------------------------
    if t == "problem_expr":
        problem = "UNKNOWN"
        function = None

        for c in node.children:
            if isinstance(c, Token):
                problem = c.value
            elif isinstance(c, Tree):
                function = node_value(c)

        return AssertionNode(
            root=UnknownNode(raw="problem_expr"),
            context=ProblemNode(problem=problem, function=function)
        )

    # ----------------------------------------------------------------------
    # FALLBACK
    # ----------------------------------------------------------------------
    return AssertionNode(root=UnknownNode(raw=f"Unhandled node: {t}"))

