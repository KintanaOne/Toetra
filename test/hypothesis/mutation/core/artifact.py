from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Artifact(Generic[T]):
    """
    Represents a DSL artifact at a specific pipeline layer.

    This is the fundamental unit manipulated by mutation testing.
    """

    value: T
    layer: str  # string | cst | ast | ir