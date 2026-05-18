from __future__ import annotations

from dataclasses import dataclass

from dsl.ast.nodes.base import ASTNode
from dsl.ast.nodes.primitives import ArgNode


@dataclass
class BackendNode(ASTNode):
    """
    Defines WHICH engine is used to verify the property.
    """

    name: str
    args: list[ArgNode]
