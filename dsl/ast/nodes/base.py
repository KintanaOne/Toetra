from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ASTNode:
    """
    Root class for all AST nodes in FORML DSL.
    Enables polymorphism and tree traversal.
    """
    pass