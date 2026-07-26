from __future__ import annotations

from dataclasses import dataclass, field

from toetra._compiler.ast.nodes.anchors import AnchorDeclarationNode
from toetra._compiler.ast.nodes.header import HeaderNode
from toetra._compiler.ast.nodes.property import PropertyNode


@dataclass
class ProgramNode:
    header: HeaderNode
    body: list[PropertyNode]
    anchors: list[AnchorDeclarationNode] = field(default_factory=list)
