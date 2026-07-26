from __future__ import annotations

from dataclasses import dataclass

from toetra._compiler.ast.nodes.base import ASTNode
from toetra._compiler.ast.nodes.primitives import (
    AttributeNode,
    ConstantNode,
    NameRefNode,
    ScalarExpressionNode,
)
from toetra._language.vocabulary.domains import EnumBoundaryKind


class DomainConstraintNode(ASTNode):
    """Base class for constraints attached to one domain subject."""

    pass


@dataclass
class SymbolLiteralNode(ASTNode):
    """Unquoted symbolic category literal used inside a finite set."""

    name: str


DomainFiniteValueNode = ConstantNode | NameRefNode | SymbolLiteralNode


@dataclass
class IntervalDomainNode(DomainConstraintNode):
    lower: ScalarExpressionNode
    upper: ScalarExpressionNode
    lower_boundary: EnumBoundaryKind
    upper_boundary: EnumBoundaryKind


@dataclass
class FiniteSetDomainNode(DomainConstraintNode):
    values: list[DomainFiniteValueNode]


@dataclass
class DomainEntryNode(ASTNode):
    subject: AttributeNode
    constraint: DomainConstraintNode


@dataclass
class DomainNode(ASTNode):
    entries: list[DomainEntryNode]
