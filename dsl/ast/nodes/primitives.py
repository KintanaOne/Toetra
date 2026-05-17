from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from dsl.semantic.types.enums import EnumDataType


PrimitiveValue = Union[str, int, float, bool, None]


@dataclass
class ArgNode:
    key: str
    value: PrimitiveValue


@dataclass
class ConstantNode:
    value: PrimitiveValue
    dtype: EnumDataType


@dataclass
class AttributeNode:
    """
    Semantic attribute access node.

    Examples:
        x.age
        x'.salary
        a            (implicit entity)

    During semantic binding:
        - entity may be rewritten
        - resolved_* fields are populated
    """

    # Raw parsed entity
    entity: str | None

    # Feature name
    feature: str

    # Full parsed path
    path: list[str]

