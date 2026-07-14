from __future__ import annotations

from dataclasses import dataclass
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


@dataclass
class AttributeExpressionIR(ScalarExpressionIR):
    entity: str
    feature: str
    dtype: EnumDataType | None = None


@dataclass
class TargetExpressionIR(ScalarExpressionIR):
    feature: str
    entity: str = "_model"
    dtype: EnumDataType | None = None


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
    Represents the entire RHS of a FORML property.

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
    High-level semantic operator coming from FORML DSL.

    Example:
        CLASSIFICATION.EQUAL()
        REGRESSION.BETWEEN()
    """

    problem: EnumProblem
    function: EnumFunction | None
    args: dict[str, Any] | None = None
