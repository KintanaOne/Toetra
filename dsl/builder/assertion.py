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

def _extract_trees(node: Tree):
    """Utility: keep only Tree children (ignore tokens safely)."""
    return [c for c in node.children if isinstance(c, Tree)]


def parse_assertion(node: Tree):
    """
    🔥 POINT CENTRAL DU DSL
    """

    if node is None:
        return UnknownNode(raw="None")

    if isinstance(node, Token):
        return UnknownNode(raw=node.value)

    t = node.data

    # ------------------------------------------------------------------------
    # implication
    # ------------------------------------------------------------------------
    if t == "assertion":
        parts = _extract_trees(node)

        if len(parts) == 1:
            return parse_assertion(parts[0])

        # safe: first => last (grammar ensures structure)
        return ImplicationNode(
            left=parse_assertion(parts[0]),
            right=parse_assertion(parts[-1])
        )

    # ------------------------------------------------------------------------
    # OR (variadic, robust)
    # ------------------------------------------------------------------------
    if t == "logic_or":
        children = _extract_trees(node)

        ops = [parse_assertion(c) for c in children]

        if not ops:
            return UnknownNode(raw="empty_or")

        if len(ops) == 1:
            return ops[0]

        return OrNode(operands=ops)

    # ------------------------------------------------------------------------
    # AND (variadic, robust)
    # ------------------------------------------------------------------------
    if t == "logic_and":
        children = _extract_trees(node)

        ops = [parse_assertion(c) for c in children]

        if not ops:
            return UnknownNode(raw="empty_and")

        if len(ops) == 1:
            return ops[0]

        return AndNode(operands=ops)

    # ------------------------------------------------------------------------
    # NOT
    # ------------------------------------------------------------------------
    if t == "logic_not":
        inner = _extract_trees(node)

        return NotNode(
            operand=parse_assertion(inner[-1]) if inner else UnknownNode("empty_not")
        )

    # ------------------------------------------------------------------------
    # atom (flatten)
    # ------------------------------------------------------------------------
    if t == "atom":
        children = _extract_trees(node)
        return parse_assertion(children[0]) if children else UnknownNode("empty_atom")

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
    # fallback
    # ------------------------------------------------------------------------
    return UnknownNode(raw=str(node))