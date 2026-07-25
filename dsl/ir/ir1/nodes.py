from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from dsl.language.vocabulary.backends import EnumBackend
from dsl.language.vocabulary.domains import EnumBoundaryKind
from dsl.language.vocabulary.functions import EnumFunction
from dsl.language.vocabulary.operators import (
    EnumArithmeticOperator,
    EnumComparisonOperator,
    EnumUnaryOperator,
)
from dsl.language.vocabulary.problems import EnumProblem
from dsl.language.vocabulary.properties import EnumProperty
from dsl.semantic.types.enums import EnumArithmeticClass, EnumDataType

# =============================================================================
# POINT AND SOURCE IDENTITIES
# =============================================================================


@dataclass(frozen=True)
class SourceSpanIR:
    """Backend-independent copy of one source range."""

    line: int
    column: int
    end_line: int
    end_column: int


@dataclass(frozen=True)
class PointFeatureIR:
    """One immutable model-input feature carried by a point identity."""

    name: str
    dtype: EnumDataType
    nullable: bool


@dataclass(frozen=True)
class PointLiteralIR:
    """One immutable concrete literal attached to an anchored point."""

    value: Any
    dtype: EnumDataType
    source_lexeme: str | None = field(default=None, compare=False)
    source_dtype: str | None = field(default=None, compare=False)


@dataclass(frozen=True)
class PointConcreteValueIR:
    """Concrete feature value retained for inline-anchor assumptions."""

    feature: str
    literal: PointLiteralIR


@dataclass(frozen=True)
class AnchorReferenceIR:
    """Single-source lookup metadata retained for runtime resolution."""

    key: str
    value: PointLiteralIR


@dataclass(frozen=True)
class AnchorResolutionIR:
    """Concrete lookup provenance retained after runtime resolution."""

    key: str
    lookup_value: PointLiteralIR
    source_kind: str
    source_reference: str | None
    row_index: str


@dataclass(frozen=True)
class PointBindingIR:
    """Stable IR1 identity for one concrete or symbolic model-input point."""

    name: str
    binding_kind: str
    lexical_depth: int = 0
    source_span: SourceSpanIR | None = None
    generated: bool = False
    feature_schema: tuple[PointFeatureIR, ...] = ()
    concrete_values: tuple[PointConcreteValueIR, ...] = ()
    reference: AnchorReferenceIR | None = None
    resolution: AnchorResolutionIR | None = None


@dataclass(frozen=True)
class QuantifierBinderIR:
    """One ordered, expanded point binder preserved in IR1."""

    quantifier: str
    point: PointBindingIR
    source_span: SourceSpanIR | None = None
    generated: bool = False


@dataclass(frozen=True, init=False)
class ModelEvaluationIR:
    """Structured identity of one model-output invocation at one point."""

    model_identity: str
    point: PointBindingIR
    output_name: str

    def __init__(
        self,
        model_identity: str,
        point: PointBindingIR,
        output_name: str | None = None,
        *,
        target_name: str | None = None,
    ) -> None:
        if (
            output_name is not None
            and target_name is not None
            and output_name != target_name
        ):
            raise ValueError(
                "ModelEvaluationIR output_name and compatibility target_name "
                "must match"
            )
        resolved = output_name if output_name is not None else target_name
        if resolved is None or not resolved.strip():
            raise ValueError("ModelEvaluationIR requires a non-empty output name")

        object.__setattr__(self, "model_identity", model_identity)
        object.__setattr__(self, "point", point)
        object.__setattr__(self, "output_name", resolved)

    @property
    def target_name(self) -> str:
        """Compatibility projection for pre-Patch-21 consumers."""

        return self.output_name


@dataclass(frozen=True)
class RestrictionProvenanceIR:
    """Source surface that introduced a canonical restriction."""

    origin: str
    source_span: SourceSpanIR | None = None


@dataclass(frozen=True)
class RestrictionIR:
    """Canonical restriction kept distinct from the property formula."""

    expression: LogicalIR
    provenance: RestrictionProvenanceIR


@dataclass(frozen=True)
class ScopeProvenanceIR:
    """Source scope form retained for diagnostics and migration."""

    source_kind: str | None
    source_span: SourceSpanIR | None = None
    legacy_compatibility: bool = False


# =============================================================================
# ROOT EXECUTION UNIT
# =============================================================================


@dataclass
class VerificationTask:
    """
    Top-level IR unit sent to a backend for verification.

    A task represents:
        - a property type (ROBUSTNESS, FAIRNESS, etc.)
        - a semantic scope (LHS context)
        - a logical query (RHS expression)
        - a target backend (Z3, ONNX checker, etc.)
    """

    property_type: EnumProperty
    scope: ScopeIR
    query: QueryIR
    backend: EnumBackend | None


# =============================================================================
# SCOPE (LHS SEMANTIC CONTEXT)
# =============================================================================


@dataclass
class ScopeIR:
    """Semantic context extracted from the left-hand side of a property.

    ``kind`` identifies the general scope family:

        pointwise
        local
        pairwise
        quantifier

    ``quantifier`` preserves the precise source-level intent for quantified
    scopes:

        forall
        exists

    It remains ``None`` for non-quantified scopes.
    """

    kind: str

    variables: dict[str, str]

    neighborhood: NeighborhoodIR | None
    domain: DomainIR | None

    quantifier: str | None = None
    points: tuple[PointBindingIR, ...] = ()
    binders: tuple[QuantifierBinderIR, ...] = ()
    restriction: RestrictionIR | None = None
    default_point: PointBindingIR | None = None
    provenance: ScopeProvenanceIR | None = None


@dataclass
class NeighborhoodIR:
    """
    Defines perturbation space around a point.
    Example: L2 ball with epsilon.
    """

    metric: str
    eps: float
    args: dict[str, Any]


class ScalarValueSource(str, Enum):
    """Origin of a scalar constant preserved for diagnostics and proofs."""

    LITERAL = "literal"
    SPECIFICATION_CONSTANT = "specification_constant"


@dataclass
class ScalarExpressionIR:
    """Base class for backend-independent scalar expression trees."""

    pass


@dataclass
class ConstantExpressionIR(ScalarExpressionIR):
    value: Any
    dtype: EnumDataType
    source_kind: ScalarValueSource = ScalarValueSource.LITERAL
    source_name: str | None = None
    source_lexeme: str | None = field(default=None, compare=False)


@dataclass
class AttributeExpressionIR(ScalarExpressionIR):
    entity: str
    feature: str
    dtype: EnumDataType | None = None
    point: PointBindingIR | None = None


@dataclass
class TargetExpressionIR(ScalarExpressionIR):
    feature: str
    entity: str = "_model"
    dtype: EnumDataType | None = None
    evaluation: ModelEvaluationIR | None = None

    @property
    def point(self) -> PointBindingIR | None:
        """Return the exact point selected by this output reference."""
        return self.evaluation.point if self.evaluation is not None else None

    @property
    def model_identity(self) -> str | None:
        """Return the declared model identity when point-aware metadata exists."""
        return self.evaluation.model_identity if self.evaluation is not None else None


@dataclass
class UnaryArithmeticExpressionIR(ScalarExpressionIR):
    operator: EnumUnaryOperator
    operand: ScalarExpressionIR
    dtype: EnumDataType | None = None
    arithmetic_class: EnumArithmeticClass | None = None


@dataclass
class BinaryArithmeticExpressionIR(ScalarExpressionIR):
    left: ScalarExpressionIR
    operator: EnumArithmeticOperator
    right: ScalarExpressionIR
    dtype: EnumDataType | None = None
    arithmetic_class: EnumArithmeticClass | None = None


@dataclass
class SymbolLiteralIR(ScalarExpressionIR):
    """Symbolic categorical literal preserved for domain membership."""

    name: str


DomainFiniteValueIR = ConstantExpressionIR | SymbolLiteralIR


@dataclass
class IntervalDomainIR:
    lower: ScalarExpressionIR
    upper: ScalarExpressionIR
    lower_boundary: EnumBoundaryKind
    upper_boundary: EnumBoundaryKind


@dataclass
class FiniteSetDomainIR:
    values: tuple[DomainFiniteValueIR, ...]


DomainConstraintIR = IntervalDomainIR | FiniteSetDomainIR


@dataclass
class DomainEntryIR:
    entity: str | None
    feature: str
    constraint: DomainConstraintIR
    dtype: EnumDataType | None = None
    point: PointBindingIR | None = field(default=None, compare=False)


@dataclass
class DomainIR:
    """Typed domain restriction preserved independently from DSL syntax."""

    entries: tuple[DomainEntryIR, ...]


# =============================================================================
# QUERY (RHS SEMANTIC EXPRESSION)
# =============================================================================


@dataclass
class QueryIR:
    """
    Represents the entire RHS of a Toetra property.

    This can be:
        - a logical expression (AND/OR/NOT/IMPLY)
        - a problem-level predicate (CLASSIFICATION.EQUAL, etc.)
    """

    expression: LogicalIR | ProblemIR


# =============================================================================
# LOGICAL IR (PURE BOOLEAN STRUCTURE)
# =============================================================================


@dataclass
class LogicalIR:
    """
    Base logical structure for boolean reasoning.

    This is the core representation used for:
        - SAT solving
        - CNF/DNF transformations
        - Z3 encoding
    """

    pass


@dataclass
class AtomicIR(LogicalIR):
    """
    Base class for logical atoms.

    Atomic nodes are leaves for NNF/CNF/DNF normalization.
    They may be DSL atoms, problem predicates, or backend-neutral
    model constraints introduced later by IR2.
    """

    pass


# =============================================================================
# LEAF COMPARISON NODE
# =============================================================================


@dataclass
class ComparisonIR(AtomicIR):
    """Atomic relation between two scalar expression trees.

    The entire comparison remains one logical atom for NNF, CNF and DNF.
    Scalar arithmetic is preserved structurally and is never rewritten by
    boolean normalization passes.
    """

    left: ScalarExpressionIR
    op: EnumComparisonOperator
    right: ScalarExpressionIR


# =============================================================================
# LOGICAL OPERATORS
# =============================================================================


@dataclass
class AndIR(LogicalIR):
    """
    Logical AND over multiple operands.
    """

    operands: list[LogicalIR]


@dataclass
class OrIR(LogicalIR):
    """
    Logical OR over multiple operands.
    """

    operands: list[LogicalIR]


@dataclass
class NotIR(LogicalIR):
    """
    Logical negation of a single operand.
    """

    operand: LogicalIR


@dataclass
class ImplyIR(LogicalIR):
    """
    Logical implication:
        A → B
    """

    left: LogicalIR
    right: LogicalIR


# =============================================================================
# PROBLEM-LEVEL SEMANTIC OPERATOR
# =============================================================================


@dataclass
class ProblemIR(AtomicIR):
    """
    High-level semantic operator coming from Toetra Specification Language.

    Example:
        CLASSIFICATION.EQUAL()
        REGRESSION.BETWEEN()
    """

    problem: EnumProblem
    function: EnumFunction | None
    args: dict[str, Any] | None = None
