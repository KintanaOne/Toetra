from lark import Tree, Token
from forml.core.utils import find_all_nodes, find_child, find_node, get_token_value
from forml.core.ast_utils import extract_attribute, node_value, clean_string, parse_attribute, parse_value


# ============================================================================
# ABSTRACTOR
# ============================================================================

def parse_abstractor(node: Tree):
    """
    abstractor = name + args

    IMPORTANT DESIGN:
    - name = Token (non-tree child)
    - args = key/value optional structure
    """
    n = find_node(node, "abstractor")
    if not n:
        return None

    name = node_value(n)
    args = {}

    args_node = find_child(n, "args")

    if args_node:
        all_nodes = find_all_nodes(args_node, "arg")
        for arg in all_nodes:
            eq = find_child(arg, "arg_identifier_eq")

            if eq:
                key = node_value(find_child(eq, "quoted_identifier"))
                val = clean_string(node_value(find_child(eq, "value")))
                if key:
                    args[key] = val
            else:
                v = node_value(arg)
                if v:
                    args[v] = v

    return {
        "name": name,
        "args": args
    }