from __future__ import annotations

from collections.abc import Iterable

from lark import Token, Tree


def program(*, declarations: str = "", body: str) -> str:
    return f"""
    model := "demo.onnx"
    target := MyTarget

    {declarations}

    [LOGIC]:
    {body}
    """


def single_tree(root: Tree, data: str) -> Tree:
    matches = list(root.find_data(data))
    assert len(matches) == 1, f"Expected one {data}, found {len(matches)}"
    return matches[0]


def direct_trees(root: Tree, data: str) -> list[Tree]:
    return [
        child
        for child in root.children
        if isinstance(child, Tree) and child.data == data
    ]


def token_text(node: Tree) -> str:
    return "".join(
        str(token) for token in node.scan_values(lambda value: isinstance(value, Token))
    )


def walk_preorder(node: Tree) -> Iterable[Tree]:
    yield node
    for child in node.children:
        if isinstance(child, Tree):
            yield from walk_preorder(child)
