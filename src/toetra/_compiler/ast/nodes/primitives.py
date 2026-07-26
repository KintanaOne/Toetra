from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union

from toetra._compiler.ast.nodes.base import ASTNode
from toetra._language.vocabulary.operators import (
    EnumArithmeticOperator,
    EnumUnaryOperator,
)
from toetra._compiler.semantic.types.enums import EnumDataType

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
    source_lexeme: str | None = field(default=None, compare=False)


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
    """Legacy scalar projection of the declared model output.

    This node preserves the public V1 regression surface ``target[point]``.
    Classification observables use :class:`ModelOutputRefNode` plus an explicit
    ``label`` or ``probability(label)`` projection instead.
    """

    point: str | None = None
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
