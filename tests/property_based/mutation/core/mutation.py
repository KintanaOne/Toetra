from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, TypeVar, Any

T = TypeVar("T")

MutationFn = Callable[[T], T]


@dataclass(frozen=True, slots=True)
class Mutation:
    """
    Pure transformation operator applied to an Artifact.

    A Mutation is stateless and deterministic by design.
    """

    name: str
    fn: MutationFn[Any]
