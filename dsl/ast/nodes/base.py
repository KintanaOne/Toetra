from __future__ import annotations

from dataclasses import dataclass, field

from dsl.semantic.runtime.annotations import SemanticAnnotations


@dataclass
class ASTNode:
    """
    Root class for all AST nodes in FORML DSL.

    Semantic annotations are attached AFTER parsing
    during semantic validation phases.
    """

    semantic: SemanticAnnotations | None = field(
        default=None,
        init=False,
        repr=False,
    )
