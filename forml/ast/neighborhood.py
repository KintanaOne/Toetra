from lark import Tree, Token
from forml.core.utils import find_child, find_all_nodes, find_node
from forml.core.ast_utils import node_value, clean_string

from typing import Optional, Dict, Tuple

# ============================================================================
# NEIGHBORHOOD
# ============================================================================

def _parse_numeric(value):
    """Try to cast value to int or float, fallback to original."""
    try:
        return int(value)
    except (TypeError, ValueError):
        pass

    try:
        return float(value)
    except (TypeError, ValueError):
        return value


def _parse_arg(arg_node):
    """
    Parse a single arg node into (key, value).
    """
    eq = find_child(arg_node, "arg_identifier_eq")

    if eq:
        key = node_value(find_child(eq, "quoted_identifier"))
        raw_val = node_value(find_child(eq, "value"))

        try:
            val = _parse_numeric(raw_val)
        except:
            val = clean_string(val)

        return key, val

    # fallback: standalone arg
    v = node_value(arg_node)
    if v:
        return v, v

    return None, None


def _parse_args(args_node):
    """Parse args node into a dict."""
    args = {}

    if not args_node:
        return args

    for arg in find_all_nodes(args_node, "arg"):
        key, val = _parse_arg(arg)

        if key is not None:
            args[key] = val

    return args


def _extract_metric(node):
    """Extract metric token from neighborhood node."""
    for child in node.children:
        if isinstance(child, Token):
            return child.value
    return None


def parse_neighborhood(node: Tree) -> Optional[Dict[str, any]]:
    """
    neighborhood = metric + args
    """
    n = find_node(node, "neighborhood")
    if not n:
        return None

    metric = _extract_metric(n)
    args_node = find_child(n, "args")
    args = _parse_args(args_node)

    return {
        "metric": metric,
        "args": args,
    }