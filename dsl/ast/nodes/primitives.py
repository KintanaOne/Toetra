from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from dsl.ast.nodes.base import ASTNode
from dsl.semantic.types.enums import EnumDataType

PrimitiveValue = Union[str, int, float, bool, None]


class ScalarExpressionNode(ASTNode):
    """Base class for scalar-valued expressions used in comparisons."""

    pass


@dataclass
class ArgNode(ASTNode):
    key: str
    value: PrimitiveValue


@dataclass
class ConstantNode(ScalarExpressionNode):
    value: PrimitiveValue
    dtype: EnumDataType


@dataclass
class AttributeNode(ScalarExpressionNode):
    """
    Semantic attribute access node.

    Examples:
        x.age
        x'.salary
        a            (implicit entity)
    """

    entity: str | None
    feature: str
    path: list[str]


@dataclass
class TargetRefNode(ScalarExpressionNode):
    """Reference to the model output declared in the FORML header."""

    name: str = "target"
