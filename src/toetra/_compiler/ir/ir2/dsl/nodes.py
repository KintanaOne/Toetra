from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING, TypeAlias

from toetra._compiler.ir.ir1.nodes import (
    AtomicIR,
    LogicalIR,
    ModelEvaluationIR,
    PointBindingIR,
    QuantifierBinderIR,
    ScopeIR,
)
from toetra._compiler.ir.ir2.enums import (
    AssumptionSource,
    NormalFormKind,
    Polarity,
    VerificationSemantics,
)
from toetra._compiler.ir.ir2.guardrails.diagnostics import IR2Diagnostic
from toetra._language.vocabulary.backends import EnumBackend
from toetra._language.vocabulary.properties import EnumProperty

if TYPE_CHECKING:
    from toetra._compiler.ir.ir2.requirements import IR2Requirements
    from toetra._models.semantics.evidence import SemanticLoweringEvidence


AtomIR2: TypeAlias = AtomicIR


@dataclass(frozen=True)
class LiteralIR2:
    """A signed atomic predicate.

    IR2 absorbs leaf negation into literal polarity instead of keeping NotIR
    around atomic predicates in CNF/DNF forms.
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
class PointIdentityMapIR2:
    """Trace one source-visible point name to its exact IR point identity."""

    source_name: str
    ir_point: PointBindingIR


@dataclass(frozen=True)
class QuantifierStructureIR2:
    """Ordered quantifier profile retained for capability matching."""

    binders: tuple[QuantifierBinderIR, ...] = ()
    binder_sequence: tuple[str, ...] = ()
    alternation_depth: int = 0

    @property
    def is_quantified(self) -> bool:
        return bool(self.binders or self.binder_sequence)

    @property
    def is_alternating(self) -> bool:
        return self.alternation_depth > 0

    @property
    def outermost_quantifier(self) -> str | None:
        return self.binder_sequence[0] if self.binder_sequence else None


@dataclass(frozen=True)
class AssumptionIR2:
    """A typed assumption used to build Γ ∧ ¬P.

    ModelEncoder produces MODEL assumptions. IR2 only carries them; it does not
    inspect sklearn/xgboost/ONNX objects directly.
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
    point_mappings: tuple[PointIdentityMapIR2, ...] = ()
    model_evaluations: tuple[ModelEvaluationIR, ...] = ()
    quantifier_structure: QuantifierStructureIR2 = field(
        default_factory=QuantifierStructureIR2
    )
    metadata: dict[str, Any] = field(default_factory=dict)
    diagnostics: tuple[IR2Diagnostic, ...] = ()
    lowering_evidence: tuple[SemanticLoweringEvidence, ...] = ()
    source_spec_formula: LogicalIR | None = None
