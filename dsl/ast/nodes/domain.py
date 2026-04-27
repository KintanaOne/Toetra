from __future__ import annotations

from dataclasses import dataclass

from dsl.ast.nodes.base import ASTNode


@dataclass
class DomainNode(ASTNode):
    name: str
    values: list[str]