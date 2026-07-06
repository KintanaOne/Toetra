from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING, TypeAlias

from dsl.ir.ir1.nodes import (
    ComparisonIR,
    LogicalIR,
    ProblemIR,
    ScopeIR,
)
from dsl.language.vocabulary.backends import EnumBackend
from dsl.language.vocabulary.properties import EnumProperty
from dsl.ir.ir2.enums import (
    AssumptionSource,
    NormalFormKind,
    Polarity,
    VerificationSemantics,
)

if TYPE_CHECKING:
    from dsl.ir.ir2.requirements import IR2Requirements


AtomIR2: TypeAlias = ComparisonIR | ProblemIR


@dataclass(frozen=True)
class LiteralIR2:
    """A signed atomic predicate.

    IR2 absorbs leaf negation into literal polarity instead of keeping NotIR
    around comparisons/problem predicates in CNF/DNF forms.
    """

    atom: AtomIR2
    polarity: Polarity = Polarity.POSITIVE


@dataclass(frozen=True)
class ClauseIR2:
    """A disjunction of literals used in CNF."""

    literals: tuple[LiteralIR2, ...]


@dataclass(frozen=True)
class TermIR2:
    """A conjunction of literals used in DNF."""

    literals: tuple[LiteralIR2, ...]


@dataclass(frozen=True)
class NNFFormulaIR2:
    """Backend-neutral formula kept as an NNF logical tree."""

    expression: LogicalIR


@dataclass(frozen=True)
class CNFFormulaIR2:
    """Conjunctive normal form: AND of OR-clauses."""

    clauses: tuple[ClauseIR2, ...]


@dataclass(frozen=True)
class DNFFormulaIR2:
    """Disjunctive normal form: OR of AND-terms."""

    terms: tuple[TermIR2, ...]


FormulaIR2: TypeAlias = NNFFormulaIR2 | CNFFormulaIR2 | DNFFormulaIR2


@dataclass(frozen=True)
class AssumptionIR2:
    """A typed assumption used to build Γ ∧ ¬P.

    ModelEncoder will later produce MODEL assumptions. IR2 only carries them;
    it does not inspect sklearn/xgboost/ONNX objects directly.
    """

    source: AssumptionSource
    formula: NNFFormulaIR2
    description: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class VerificationTaskIR2:
    """Backend-neutral verification task.

    spec_formula is the property P expressed by the DSL and normalized to NNF.
    verification_condition is the internal condition Γ ∧ ¬P, optionally
    converted to CNF or DNF when useful and safe.
    """

    property_type: EnumProperty
    scope: ScopeIR
    backend: EnumBackend | None

    assumptions: tuple[AssumptionIR2, ...]
    spec_formula: NNFFormulaIR2
    verification_condition: FormulaIR2

    semantics: VerificationSemantics
    normal_form: NormalFormKind
    requirements: IR2Requirements
    metadata: dict[str, Any] = field(default_factory=dict)
