from lark import Tree
from dsl.builder.core.utils import find_child, find_all_nodes, find_node
from dsl.builder.core.ast_utils import node_value, clean_string

from dsl.ast.nodes.backends import BackendNode
from dsl.ast.nodes.primitives import ArgNode

# ============================================================================
# backend
# ============================================================================

def parse_backend(node: Tree):
    """
    backend = name + args

    IMPORTANT DESIGN:
    - name = Token (non-tree child)
    - args = key/value optional structure
    """
    n = find_node(node, "backend")
    if not n:
        return None

    name = node_value(n)
    args: list[ArgNode] = []

    args_node = find_child(n, "args")

    if args_node:
        for arg in find_all_nodes(args_node, "arg"):
            eq = find_child(arg, "arg_identifier_eq")

            if eq:
                key = node_value(find_child(eq, "quoted_identifier"))
                raw_val = node_value(find_child(eq, "value"))
                val = clean_string(raw_val)

                if key:
                    args.append(
                        ArgNode(
                            key=key,
                            value=val
                        )
                    )
            else:
                v = node_value(arg)
                if v:
                    args.append(
                        ArgNode(
                            key=v,
                            value=v
                        )
                    )

    return BackendNode(
        name=name,
        args=args
    )