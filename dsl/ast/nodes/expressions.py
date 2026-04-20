from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from dsl.ast.nodes.neighborhood import NeighborhoodNode
from dsl.ast.nodes.domain import DomainNode


# ============================================================================
# BASE
# ============================================================================

@dataclass
class ExpressionNode:
    """
    Base class for all scope/expression constructs.
    Represents WHERE / IN WHICH CONTEXT a property is evaluated.
    """
    pass


# ============================================================================
# AT EXPRESSION
# ============================================================================

@dataclass
class AtExprNode(ExpressionNode):
    variable: str
    neighborhood: NeighborhoodNode
    domain: DomainNode


# ============================================================================
# PAIRWISE EXPRESSION
# ============================================================================

@dataclass
class PairwiseExprNode(ExpressionNode):
    pair: str
    neighborhood: NeighborhoodNode
    domain: DomainNode


# ============================================================================
# CHECK AT
# ============================================================================

@dataclass
class CheckAtExprNode(ExpressionNode):
    variable: str


# ============================================================================
# QUANTIFIER
# ============================================================================

@dataclass
class QuantifierExprNode(ExpressionNode):
    quantifier: str
    domain: DomainNode