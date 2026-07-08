from __future__ import annotations

from dataclasses import dataclass

from dsl.ast.nodes.base import ASTNode
from dsl.ast.nodes.primitives import ArgNode
from dsl.language.vocabulary.backends import EnumBackend


@dataclass
class BackendNode(ASTNode):
    """
    Defines WHICH engine is used to verify the property.
    """

    name: EnumBackend
    args: list[ArgNode]
