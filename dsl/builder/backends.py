from lark import Tree
from dsl.builder.core.utils import (
    find_child,
    find_all_nodes,
    find_node,
    get_node_name_or_value,
)
from dsl.builder.core.ast_utils import node_value, clean_string

from dsl.ast.nodes.backends import BackendNode
from dsl.ast.nodes.primitives import ArgNode

# ============================================================================
# backend
# ============================================================================


def parse_backend(node: Tree | None):
    if node is None:
        return None

    n = find_node(node, "backend")
    if n is None:
        return None

    name_node = n.children[0]
    name = get_node_name_or_value(name_node)

    if name is None:
        raise ValueError("Backend name missing")

    args: list[ArgNode] = []

    args_node = find_child(n, "args")

    if args_node:
        for arg in find_all_nodes(args_node, "arg"):
            eq = find_child(arg, "arg_identifier_eq")

            if eq:
                key = node_value(find_child(eq, "quoted_identifier"))
                val = clean_string(node_value(find_child(eq, "value")))

                if key is None or val is None:
                    raise ValueError("Invalid backend arg")

                args.append(ArgNode(key=key, value=val))

    return BackendNode(name=name, args=args)
