from lark import Tree, Token

from toetra._compiler.ast.nodes.backends import BackendNode
from toetra._compiler.ast.nodes.primitives import ArgNode
from toetra._compiler.builder.core.source import with_source_span
from toetra._compiler.builder.core.utils import (
    find_child,
    find_all_nodes,
    find_node,
    get_node_name_or_value,
)
from toetra._compiler.builder.core.ast_utils import (
    clean_string,
    node_value,
    parse_value,
)
from toetra._language.vocabulary.backends import EnumBackend


def _extract_backend_name(node: Tree) -> str:
    """
    Extract backend name from a backend node.

    Expected CST shape after protected words:
        backend
          USING
          Z3

    The USING token must be ignored.
    """

    for child in node.children:
        if isinstance(child, Token):
            if child.type == "USING":
                continue

            return child.value

        if isinstance(child, Tree):
            value = get_node_name_or_value(child)

            if value is not None:
                return value

    raise ValueError("Backend name missing")


def parse_backend(node: Tree | None) -> BackendNode | None:
    if node is None:
        return None

    backend_node = find_node(node, "backend")

    if backend_node is None:
        return None

    raw_name = _extract_backend_name(backend_node)

    try:
        name = EnumBackend.from_str(raw_name)
    except ValueError as e:
        raise ValueError(f"Unsupported backend '{raw_name}'") from e

    args: list[ArgNode] = []
    seen: set[str] = set()

    args_node = find_child(backend_node, "args")
    if args_node is not None:
        for arg in find_all_nodes(args_node, "arg"):
            eq = find_child(arg, "arg_identifier_eq")
            if eq is None:
                raise ValueError(
                    "Backend arguments must use the explicit name=value form"
                )

            key = clean_string(node_value(find_child(eq, "quoted_identifier")))
            value_node = find_child(eq, "value")
            if key is None or value_node is None:
                raise ValueError("Invalid backend argument")
            if key in seen:
                raise ValueError(f"Duplicate backend argument '{key}'")
            seen.add(key)
            argument = ArgNode(key=key, value=parse_value(value_node).value)
            args.append(with_source_span(argument, arg))

    return with_source_span(BackendNode(name=name, args=args), backend_node)
