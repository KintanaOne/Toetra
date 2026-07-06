from __future__ import annotations

from enum import Enum


class NormalFormKind(str, Enum):
    """Supported logical forms at IR2 level.

    NNF is the safe fallback form. CNF and DNF are optional optimized forms
    selected when they are useful and reasonably small.
    """

    NNF = "nnf"
    CNF = "cnf"
    DNF = "dnf"


class VerificationSemantics(str, Enum):
    """How the verification condition must be interpreted.

    REFUTATION means FORML proves a property P by checking whether Γ ∧ ¬P is
    satisfiable. If it is impossible, then P holds under assumptions Γ.
    """

    REFUTATION = "refutation"
    DIRECT = "direct"


class Polarity(str, Enum):
    """Polarity of a literal inside CNF/DNF formulas."""

    POSITIVE = "positive"
    NEGATIVE = "negative"


class AssumptionSource(str, Enum):
    """Origin of an assumption used by an IR2 verification condition."""

    MODEL = "model"
    SCOPE = "scope"
    DOMAIN = "domain"
    USER = "user"
    INTERNAL = "internal"
