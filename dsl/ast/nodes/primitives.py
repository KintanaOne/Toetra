from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class ArgNode:
    key: str
    value: str | int | float | bool | None

@dataclass
class ConstantNode:
    value: Any
    dtype: str  # "int", "float", "string"


@dataclass
class AttributeNode:
    entity: Optional[str]
    feature: str
    path: List[str]