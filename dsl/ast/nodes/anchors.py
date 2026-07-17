from __future__ import annotations

from dataclasses import dataclass

from dsl.ast.nodes.base import ASTNode
from dsl.ast.nodes.primitives import ConstantNode


class AnchorBindingNode(ASTNode):
    """Base class for concrete point bindings declared by ``anchor``."""


@dataclass
class AnchorEntryNode(ASTNode):
    """One ordered feature/value entry from an inline anchor."""

    feature: str
    value: ConstantNode


@dataclass
class InlineAnchorBindingNode(AnchorBindingNode):
    """Inline concrete point preserving entry order and duplicate spellings."""

    entries: list[AnchorEntryNode]


@dataclass
class AnchorReferenceArgumentNode(ASTNode):
    """One ordered named argument from a ``ref(...)`` binding."""

    name: str
    value: ConstantNode


@dataclass
class AnchorReferenceBindingNode(AnchorBindingNode):
    """Single-source external point reference preserved for later validation."""

    arguments: list[AnchorReferenceArgumentNode]


@dataclass
class AnchorDeclarationNode(ASTNode):
    """Global immutable point declaration."""

    name: str
    binding: AnchorBindingNode
