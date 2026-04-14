from lark import Tree, Token
from forml.core.utils import find_child, find_node, get_token_value
from forml.core.ast_utils import extract_attribute, node_value, clean_string, parse_attribute, parse_value


def build_logic_expr(node: Tree) -> dict:
    """
    Build a structured comparison expression.
    """

    attribute_node = find_node(node, "attribute")
    value_node = find_node(node, "value")
    op_node = find_node(node, "logic_operation")

    return {
        "kind": "comparison",
        "left": parse_attribute(attribute_node),
        "op": get_token_value(op_node),
        "right": parse_value(value_node),
    }


# ============================================================================
# ASSERTION ENGINE (FUTURE PROOF CORE)
# ============================================================================

def parse_assertion(node: Tree):
    """
    🔥 POINT CENTRAL DU DSL

    Design principle :
    ------------------
    On ne dépend JAMAIS de :
        - positions children[i]
        - heuristiques OR/AND
        - structure fragile

    Tout est basé sur node.data (grammaire Lark)
    """

    if node is None:
        return {}

    t = node.data

    # ------------------------------------------------------------------------
    # implication
    # ------------------------------------------------------------------------
    if t == "assertion":
        parts = [c for c in node.children if isinstance(c, Tree)]

        if len(parts) == 1:
            return parse_assertion(parts[0])

        return {
            "kind": "implication",
            "left": parse_assertion(parts[0]),
            "right": parse_assertion(parts[-1])
        }

    # ------------------------------------------------------------------------
    # OR (variadic)
    # ------------------------------------------------------------------------
    if t == "logic_or":
        ops = [parse_assertion(c) for c in node.children if isinstance(c, Tree)]
        return {
            "kind": "or", 
            "operands": ops
            } if len(ops) > 1 else ops[0]

    # ------------------------------------------------------------------------
    # AND (variadic)
    # ------------------------------------------------------------------------
    if t == "logic_and":
        ops = [parse_assertion(c) for c in node.children if isinstance(c, Tree)]
        return {
            "kind": "and", 
            "operands": ops
            } if len(ops) > 1 else ops[0]

    # ------------------------------------------------------------------------
    # NOT
    # ------------------------------------------------------------------------
    if t == "logic_not":
        inner = [c for c in node.children if isinstance(c, Tree)]
        return {
            "kind": "not",
            "operand": parse_assertion(inner[-1]) if inner else None
        }

    # ------------------------------------------------------------------------
    # atom wrapper
    # ------------------------------------------------------------------------
    if t == "atom":
        return parse_assertion(node.children[0])

    # ------------------------------------------------------------------------
    # comparison (IMPORTANT FIX x0.feature1 OK)
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

        return {
            "kind": "problem",
            "problem": problem,
            "function": function
        }

    return {
        "kind": "unknown", 
        "raw": str(node)
        }