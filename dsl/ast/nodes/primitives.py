from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from dsl.ast.nodes.base import ASTNode
from dsl.semantic.types.enums import EnumDataType

PrimitiveValue = Union[str, int, float, bool, None]


@dataclass
class ArgNode(ASTNode):
    key: str
    value: PrimitiveValue


@dataclass
class ConstantNode(ASTNode):
    value: PrimitiveValue
    dtype: EnumDataType


@dataclass
class AttributeNode(ASTNode):
    """
    Semantic attribute access node.

    Examples:
        x.age
        x'.salary
        a            (implicit entity)

    During semantic binding:
        - semantic.resolved_entity is populated
        - semantic.resolved_path is populated
        - semantic.resolved_symbol may be populated
        - semantic.resolved_type may be populated later by schema-aware validation
    """

    # Raw parsed entity
    entity: str | None

    # Feature name
    feature: str

    # Full parsed path
    path: list[str]
