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
    """How a verification condition must be interpreted.

    REFUTATION
        FORML searches for a violation of a property P by solving:

            Gamma AND NOT P

        Solver interpretation:
            SAT     -> a counterexample exists
            UNSAT   -> the property is proved under Gamma
            UNKNOWN -> no conclusion can be drawn

    SATISFACTION
        FORML searches for a value satisfying a property P by solving:

            Gamma AND P

        Solver interpretation:
            SAT     -> a witness exists
            UNSAT   -> no witness exists
            UNKNOWN -> no conclusion can be drawn

    These semantics describe the meaning of the backend query. They are
    distinct from the source-level FORML quantifier and from the final
    verification status.
    """

    REFUTATION = "refutation"
    SATISFACTION = "satisfaction"


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
