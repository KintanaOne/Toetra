from __future__ import annotations

from dataclasses import dataclass, field

from dsl.ast.nodes.anchors import AnchorDeclarationNode
from dsl.ast.nodes.header import HeaderNode
from dsl.ast.nodes.property import PropertyNode


@dataclass
class ProgramNode:
    header: HeaderNode
    body: list[PropertyNode]
    anchors: list[AnchorDeclarationNode] = field(default_factory=list)
