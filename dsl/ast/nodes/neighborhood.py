from __future__ import annotations

from dataclasses import dataclass

from dsl.ast.nodes.base import ASTNode
from dsl.ast.nodes.primitives import ArgNode


@dataclass
class NeighborhoodNode(ASTNode):
    metric: str
    args: list[ArgNode]
