from lark import Tree, Token
from dsl.ast.nodes.assertion import (
    AndNode,
    ComparisonNode,
    OrNode,
    NotNode,
    ProblemNode,
    UnknownNode,
)
from dsl.ast.nodes.implication import ImplicationNode
from dsl.builder.core.utils import find_node, get_token_value
from dsl.builder.core.ast_utils import parse_attribute, node_value, parse_value


def build_logic_expr(node: Tree) -> ComparisonNode:
    """
    Build a structured comparison expression.
    """
    attribute_node = find_node(node, "attribute")
    value_node = find_node(node, "value")
    op_node = find_node(node, "logic_operation")

    return ComparisonNode(
        left=parse_attribute(attribute_node),
        op=get_token_value(op_node),
        right=parse_value(value_node),
    )


# ============================================================================
# ASSERTION ENGINE (FUTURE PROOF CORE)
# ============================================================================

def parse_assertion(node: Tree):
    """
    🔥 POINT CENTRAL DU DSL

    Design principe :
    ------------------
    it does not rely on the position of children but only on their type (data) and structure.
    This makes it more robust to changes in the grammar and allows for more complex expressions.
    It also allows for more natural expressions (e.g., A AND B OR C is parsed as (A AND B) OR C without needing to enforce parentheses).:
    """

    if node is None:
        return UnknownNode(raw="None")

    t = node.data

    # ------------------------------------------------------------------------
    # implication
    # ------------------------------------------------------------------------
    if t == "assertion":
        parts = [c for c in node.children if isinstance(c, Tree)]

        if len(parts) == 1:
            return parse_assertion(parts[0])

        return ImplicationNode(
            left=parse_assertion(parts[0]),
            right=parse_assertion(parts[-1])
        )

    # ------------------------------------------------------------------------
    # OR (variadic)
    # ------------------------------------------------------------------------
    if t == "logic_or":
        ops = [parse_assertion(c) for c in node.children if isinstance(c, Tree)]

        return ops[0] if len(ops) == 1 else OrNode(operands=ops)

    # ------------------------------------------------------------------------
    # AND (variadic)
    # ------------------------------------------------------------------------
    if t == "logic_and":
        ops = [parse_assertion(c) for c in node.children if isinstance(c, Tree)]

        return ops[0] if len(ops) == 1 else AndNode(operands=ops)

    # ------------------------------------------------------------------------
    # NOT
    # ------------------------------------------------------------------------
    if t == "logic_not":
        inner = [c for c in node.children if isinstance(c, Tree)]

        return NotNode(
            operand=parse_assertion(inner[-1]) if inner else UnknownNode("empty_not")
        )
    # ------------------------------------------------------------------------
    # atom 
    # ------------------------------------------------------------------------
    if t == "atom":
        return parse_assertion(node.children[0])

    # ------------------------------------------------------------------------
    # comparison 
    # ------------------------------------------------------------------------
    if t == "logic_expr":
        return build_logic_expr(node)

    # ------------------------------------------------------------------------
    # problem expr
    # ------------------------------------------------------------------------
    if t == "problem_expr":
        problem = None
        function = None

        for c in node.children:
            if isinstance(c, Token):
                problem = c.value
            elif isinstance(c, Tree):
                function = node_value(c)

        return ProblemNode(
            problem=problem,
            function=function
        )

    # ------------------------------------------------------------------------
    # fallback expr
    # ------------------------------------------------------------------------
    return UnknownNode(raw=str(node))