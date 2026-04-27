from __future__ import annotations

from dataclasses import dataclass
from typing import Union


PrimitiveValue = Union[str, int, float, bool, None]


@dataclass
class ArgNode:
    key: str
    value: PrimitiveValue


@dataclass
class ConstantNode:
    value: PrimitiveValue
    dtype: str  # TODO: remplacer par Enum


@dataclass
class AttributeNode:
    entity: str | None
    feature: str
    path: list[str]