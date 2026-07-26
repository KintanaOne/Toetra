from enum import Enum


class EnumBoundaryKind(str, Enum):
    """Interval endpoint inclusion kind used by typed domain nodes."""

    OPEN = "open"
    CLOSED = "closed"
