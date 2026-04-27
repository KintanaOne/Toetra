from __future__ import annotations

from dataclasses import dataclass
from typing import Union

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
    pair: str
    neighborhood: NeighborhoodNode
    domain: DomainNode | None = None


@dataclass
class CheckAtExprNode(ExpressionNode):
    variable: str


@dataclass
class QuantifierExprNode(ExpressionNode):
    quantifier: str
    domain: DomainNode | None