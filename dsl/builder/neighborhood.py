from lark import Tree, Token
from dsl.ast.nodes.neighborhood import NeighborhoodNode
from dsl.ast.nodes.primitives import ArgNode
from dsl.builder.core.utils import find_child, find_all_nodes, find_node
from dsl.builder.core.ast_utils import node_value, clean_string
from dsl.builder.core.strict import require_node, require_value

from typing import List, Any

# ============================================================================
# NEIGHBORHOOD PARSER
# ============================================================================
# This module parses a Neighborhood AST node in a strict manner.
# All invalid or missing elements raise immediate errors to guarantee
# AST consistency for downstream processing.
# ============================================================================


# ---------------------------------------------------------------------------
# Numeric parsing helper
# ---------------------------------------------------------------------------
def _parse_numeric(value: Any) -> Any:
    """
    Try to convert a value into int or float.
    Falls back to original value if conversion fails.
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        pass

    try:
        return float(value)
    except (TypeError, ValueError):
        return value


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
def _parse_arg(arg_node: Tree) -> ArgNode | None:
    """
    Parse a single argument node into an ArgNode.
    """

    eq = find_child(arg_node, "arg_identifier_eq")
    if eq is None:
        return None

    key_node = find_child(eq, "quoted_identifier")
    val_node = find_child(eq, "value")

    key = require_value(node_value(key_node), "Missing argument key")

    raw_val = node_value(val_node)
    if raw_val is None:
        raise ValueError("Missing argument value")

    # Try numeric conversion first, fallback to cleaned string
    try:
        val = _parse_numeric(raw_val)
    except Exception:
        val = clean_string(raw_val)

    return ArgNode(key=key, value=val)


# ---------------------------------------------------------------------------
# Args parsing
# ---------------------------------------------------------------------------
def _parse_args(args_node: Tree | None) -> List[ArgNode]:
    """
    Parse args node into a list of ArgNode.
    """

    if args_node is None:
        return []

    args: List[ArgNode] = []

    for arg in find_all_nodes(args_node, "arg"):
        parsed = _parse_arg(arg)
        if parsed is not None:
            args.append(parsed)

    return args


# ---------------------------------------------------------------------------
# Metric extraction
# ---------------------------------------------------------------------------
def _extract_metric(node: Tree) -> str:
    """
    Extract metric token from a neighborhood node.
    """

    if not node.children:
        raise ValueError("Neighborhood node is empty")

    for child in node.children:
        if isinstance(child, Token):
            return child.value

    raise ValueError("No metric token found in neighborhood")


# ---------------------------------------------------------------------------
# Main parser
# ---------------------------------------------------------------------------
def parse_neighborhood(node: Tree) -> NeighborhoodNode:
    """
    Parse a neighborhood expression:
        neighborhood = metric + args
    """

    n = require_node(find_node(node, "neighborhood"), "Neighborhood node not found")

    metric = _extract_metric(n)

    args_node = find_child(n, "args")
    args = _parse_args(args_node)

    return NeighborhoodNode(metric=metric, args=args)
