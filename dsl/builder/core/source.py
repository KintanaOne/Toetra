from __future__ import annotations

from typing import TypeVar

from lark import Tree

from dsl.ast.nodes.base import ASTNode
from dsl.ast.nodes.source import source_span_from_tree

TNode = TypeVar("TNode", bound=ASTNode)


def with_source_span(node: TNode, tree: Tree) -> TNode:
    """Attach CST provenance to an AST node without changing its constructor."""
    node.source_span = source_span_from_tree(tree)
    return node
