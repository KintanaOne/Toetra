# forml/transformer/helper.py

from forml.transformer.nodes import *


def print_tree(node, indent="", is_last=True):
    """Pretty print a Node tree like the Unix 'tree' command."""

    branch = "└── " if is_last else "├── "
    print(indent + branch + format_node(node))

    indent += "    " if is_last else "│   "

    children = get_children(node)

    for i, child in enumerate(children):
        is_child_last = i == len(children) - 1
        print_tree(child, indent, is_child_last)


def get_children(node):
    children = []

    if hasattr(node, "__dict__"):
        for value in node.__dict__.values():
            if isinstance(value, Node):
                children.append(value)
            elif isinstance(value, list):
                children.extend([v for v in value if isinstance(v, Node)])

    return children


def format_node(node):
    """Customize how each node is displayed."""

    if isinstance(node, Program):
        return "Program"

    if isinstance(node, Header):
        return "Header"

    if isinstance(node, Body):
        return "Body"

    if isinstance(node, PropertySection):
        return "PropertySection"

    if isinstance(node, Property):
        return f"Property ({node.property_type})"

    if isinstance(node, UniversalExpr):
        return f"UniversalExpr ({node.quantifier} {node.set})"

    if isinstance(node, ProblemExpr):
        return f"ProblemExpr ({node.problem})"

    if isinstance(node, FunctionExpr):
        return f"FunctionExpr ({node.function.name})"

    if isinstance(node, TargetDeclaration):
        return f"Target ({node.target})"

    if isinstance(node, ModelDeclaration):
        return f"Model ({node.path})"

    if isinstance(node, Assertion):
        return "Assertion"

    return node.__class__.__name__