from __future__ import annotations

from dataclasses import dataclass

from dsl.ast.nodes.assertion import LogicalNode
from dsl.ast.nodes.base import ASTNode
from dsl.ast.nodes.domain import DomainNode
from dsl.ast.nodes.neighborhood import (
    NeighborhoodMembershipNode,
    NeighborhoodNode,
)


@dataclass
class ExpressionNode(ASTNode):
    """Source-level context in which a property assertion is written."""


@dataclass
class DirectExprNode(ExpressionNode):
    """Marker for a property containing a direct assertion and no source scope."""


@dataclass
class RestrictionNode(ASTNode):
    """A source ``where`` restriction kept separate from the assertion."""

    expression: LogicalNode | NeighborhoodMembershipNode


@dataclass
class AtExprNode(ExpressionNode):
    variable: str
    neighborhood: NeighborhoodNode | None
    domain: DomainNode | None
    local_membership: NeighborhoodMembershipNode | None = None


@dataclass
class PairwiseExprNode(ExpressionNode):
    left: str
    right: str
    neighborhood: NeighborhoodNode
    domain: DomainNode | None = None

    @property
    def pair(self) -> str:
        """Backward-compatible textual representation."""
        return f"{self.left} ~ {self.right}"


@dataclass
class CheckAtExprNode(ExpressionNode):
    variable: str


@dataclass
class QuantifierBinderNode(ASTNode):
    """One ordered quantifier clause with its source identifier list."""

    quantifier: str
    variables: list[str]


@dataclass
class QuantifierExprNode(ExpressionNode):
    """Ordered source binder chain with optional domain and restriction."""

    binders: list[QuantifierBinderNode]
    domain: DomainNode | None
    restriction: RestrictionNode | None = None

    def _legacy_single_binding(self) -> tuple[str, str]:
        if len(self.binders) != 1 or len(self.binders[0].variables) != 1:
            raise ValueError(
                "Legacy quantifier projection requires exactly one binder and one point"
            )
        binder = self.binders[0]
        return binder.quantifier, binder.variables[0]

    @property
    def quantifier(self) -> str:
        """Compatibility projection for the pre-P15 one-point pipeline."""
        quantifier, _ = self._legacy_single_binding()
        return quantifier

    @property
    def variable(self) -> str:
        """Compatibility projection for the pre-P15 one-point pipeline."""
        _, variable = self._legacy_single_binding()
        return variable
