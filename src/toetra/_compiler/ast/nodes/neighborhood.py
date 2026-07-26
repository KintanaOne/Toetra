from __future__ import annotations

from dataclasses import dataclass

from toetra._compiler.ast.nodes.base import ASTNode
from toetra._compiler.ast.nodes.primitives import ArgNode, ScalarExpressionNode


@dataclass
class NeighborhoodNode(ASTNode):
    """Legacy metric neighborhood surface retained for compatibility."""

    metric: str
    args: list[ArgNode]


@dataclass
class NeighborhoodMembershipNode(ASTNode):
    """Structured natural membership ``candidate in neighborhood(of=anchor, ...)``."""

    candidate: str
    anchor: str
    metric: str
    epsilon: ScalarExpressionNode
