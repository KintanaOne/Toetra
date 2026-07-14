from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from dsl.ast.nodes.base import ASTNode
from dsl.language.vocabulary.operators import (
    EnumArithmeticOperator,
    EnumUnaryOperator,
)
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
class NameRefNode(ScalarExpressionNode):
    """Unresolved bare identifier used in a scalar-expression position.

    The builder deliberately preserves a bare name without deciding whether it
    denotes a specification constant or an implicit feature. Semantic binding
    owns that context-aware resolution.
    """

    name: str


@dataclass
class AttributeNode(ScalarExpressionNode):
    """
    Semantic attribute access node.

    Examples:
        x.age
        x'.salary
        a            (implicit entity in legacy/bound AST paths)
    """

    entity: str | None
    feature: str
    path: list[str]


@dataclass
class TargetRefNode(ScalarExpressionNode):
    """Reference to the model output declared in the FORML header."""

    name: str = "target"


@dataclass
class UnaryArithmeticNode(ScalarExpressionNode):
    """Unary scalar arithmetic expression such as ``-x0.a``."""

    operator: EnumUnaryOperator
    operand: ScalarExpressionNode


@dataclass
class BinaryArithmeticNode(ScalarExpressionNode):
    """Binary scalar arithmetic expression preserving operand order."""

    left: ScalarExpressionNode
    operator: EnumArithmeticOperator
    right: ScalarExpressionNode
