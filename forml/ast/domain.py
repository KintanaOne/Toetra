from lark import Tree
from forml.core.utils import find_child, find_all_nodes, find_node
from forml.core.ast_utils import node_value, clean_string


# ============================================================================
# DOMAIN
# ============================================================================

def parse_domain(node: Tree) -> dict:
    """
    domain = name + values[]
    """
    domain = find_node(node, "domain")
    if not domain:
        return None

    return {
        "name": node_value(find_child(domain, "identifier")),
        "values": [
            clean_string(node_value(v))
            for v in find_all_nodes(domain, "value")
        ]
    }
