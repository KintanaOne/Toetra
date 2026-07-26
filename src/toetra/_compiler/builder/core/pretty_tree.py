from typing import Any


def pretty_tree(node: Any, prefix: str = "", is_last: bool = True) -> str:
    """
    Pretty print AST as a tree (like Lark .pretty()).

    Example:
    ProgramNode
    ├── header
    │   └── HeaderNode
    └── body
        └── PropertyNode
    """

    connector = "└── " if is_last else "├── "
    line = prefix + connector + _node_label(node)

    lines = [line]

    children = _get_children(node)

    if children:
        new_prefix = prefix + ("    " if is_last else "│   ")

        for i, (key, child) in enumerate(children):
            last = i == len(children) - 1

            if key is not None:
                # Print field name
                lines.append(new_prefix + ("└── " if last else "├── ") + f"{key}")

                child_prefix = new_prefix + ("    " if last else "│   ")
                lines.append(pretty_tree(child, child_prefix, True))
            else:
                lines.append(pretty_tree(child, new_prefix, last))

    return "\n".join(lines)


def _node_label(node: Any) -> str:
    if node is None:
        return "None"

    if isinstance(node, (str, int, float, bool)):
        return str(node)

    return node.__class__.__name__


def _get_children(node: Any):
    """
    Extract children as (key, value) pairs.
    """

    if node is None:
        return []

    if isinstance(node, list):
        return [(None, item) for item in node]

    if hasattr(node, "__dict__"):
        return [(k, v) for k, v in node.__dict__.items()]

    return []
