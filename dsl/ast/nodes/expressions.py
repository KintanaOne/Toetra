from __future__ import annotations

from dataclasses import dataclass

from dsl.ast.nodes.base import ASTNode
from dsl.ast.nodes.neighborhood import NeighborhoodNode
from dsl.ast.nodes.domain import DomainNode


@dataclass
class ExpressionNode(ASTNode):
    """WHERE a property is evaluated."""

    pass


@dataclass
class AtExprNode(ExpressionNode):
    variable: str
    neighborhood: NeighborhoodNode | None
    domain: DomainNode | None


@dataclass
class PairwiseExprNode(ExpressionNode):
    left: str
    right: str
    neighborhood: NeighborhoodNode
    domain: DomainNode | None = None

    @property
    def pair(self) -> str:
        """
        Backward-compatible textual representation.

        Internal code should prefer `left` and `right`.
        """
        return f"{self.left} ~ {self.right}"


@dataclass
class CheckAtExprNode(ExpressionNode):
    variable: str


@dataclass
class QuantifierExprNode(ExpressionNode):
    quantifier: str
    variable: str
    domain: DomainNode | None
