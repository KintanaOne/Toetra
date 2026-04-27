# dsl/utils/pretty.py

from typing import Any


def pretty(node: Any, indent: int = 0) -> str:
    """
    Generic pretty printer for AST nodes.

    - Handles primitives (str, int, float, bool)
    - Handles lists
    - Handles dataclasses / objects via __dict__
    """

    pad = "  " * indent

    # None
    if node is None:
        return f"{pad}None"

    # Primitive types
    if isinstance(node, (str, int, float, bool)):
        return f"{pad}{node}"

    # List
    if isinstance(node, list):
        if not node:
            return f"{pad}[]"

        lines = []
        for item in node:
            lines.append(pretty(item, indent))
        return "\n".join(lines)

    # AST Node (dataclass or object)
    if hasattr(node, "__dict__"):
        lines = [f"{pad}{node.__class__.__name__}"]

        for key, value in node.__dict__.items():
            lines.append(f"{pad}  {key}:")
            lines.append(pretty(value, indent + 2))

        return "\n".join(lines)

    # Fallback
    return f"{pad}{repr(node)}"