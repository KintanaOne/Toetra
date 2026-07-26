from __future__ import annotations

from dataclasses import dataclass

from toetra._compiler.ast.nodes.base import ASTNode
from toetra._compiler.ast.nodes.primitives import ArgNode
from toetra._language.vocabulary.backends import EnumBackend


@dataclass
class BackendNode(ASTNode):
    """
    Defines WHICH engine is used to verify the property.
    """

    name: EnumBackend
    args: list[ArgNode]
