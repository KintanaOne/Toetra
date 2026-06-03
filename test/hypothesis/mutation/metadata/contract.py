from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class PreservationLevel(Enum):
    """
    Degree of structural or semantic preservation.
    """

    NONE = auto()
    PARTIAL = auto()
    FULL = auto()


@dataclass(frozen=True, slots=True)
class MutationContract:
    """
    Formal guarantees provided by a mutation.

    This replaces multiple boolean 'preserves_*' flags.
    """

    cst: PreservationLevel
    ast: PreservationLevel
    typing: PreservationLevel
    semantics: PreservationLevel