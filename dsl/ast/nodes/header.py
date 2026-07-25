from __future__ import annotations

from dataclasses import dataclass, field

from dsl.ast.nodes.base import ASTNode
from dsl.ast.nodes.primitives import ConstantNode


@dataclass
class SpecificationConstantDeclarationNode(ASTNode):
    """Immutable scalar literal declared in a Toetra program header."""

    name: str
    value: ConstantNode


@dataclass
class HeaderNode:
    model: str
    target: str
    specification_constants: list[SpecificationConstantDeclarationNode] = field(
        default_factory=list
    )
