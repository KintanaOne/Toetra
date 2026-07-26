from __future__ import annotations

from dataclasses import dataclass

from toetra._compiler.ast.nodes.assertion import AssertionNode
from toetra._compiler.ast.nodes.backends import BackendNode
from toetra._compiler.ast.nodes.base import ASTNode
from toetra._compiler.ast.nodes.expressions import ExpressionNode
from toetra._language.vocabulary.properties import EnumProperty


@dataclass
class PropertyNode(ASTNode):
    type: EnumProperty
    rule: PropertyRuleNode
    backend: BackendNode | None


@dataclass
class PropertyRuleNode(ASTNode):
    scope: ExpressionNode
    assertion: AssertionNode
