from __future__ import annotations

from dataclasses import dataclass

from dsl.ast.nodes.assertion import AssertionNode
from dsl.ast.nodes.backends import BackendNode
from dsl.ast.nodes.expressions import ExpressionNode
from dsl.language.vocabulary.properties import EnumProperty


@dataclass
class PropertyNode:
    type: EnumProperty
    rule: PropertyRuleNode
    backend: BackendNode | None


@dataclass
class PropertyRuleNode:
    scope: ExpressionNode
    assertion: AssertionNode