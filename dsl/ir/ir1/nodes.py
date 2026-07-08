from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dsl.language.vocabulary.backends import EnumBackend
from dsl.language.vocabulary.functions import EnumFunction
from dsl.language.vocabulary.operators import EnumComparisonOperator
from dsl.language.vocabulary.problems import EnumProblem
from dsl.language.vocabulary.properties import EnumProperty
from dsl.semantic.types.enums import EnumDataType

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
    """
    Semantic context extracted from the LHS of a FORML property.

    Defines:
        - variables (anchor, perturbation, symbolic variables)
        - neighborhood constraints (e.g. L2 epsilon ball)
        - optional domain constraints
    """

    kind: str  # "local", "pairwise", "quantifier", "pointwise"

    variables: dict[str, str]
    # Example:
    # {
    #   "x": "anchor",
    #   "x'": "perturbation"
    # }

    neighborhood: NeighborhoodIR | None
    domain: DomainIR | None


@dataclass
class NeighborhoodIR:
    """
    Defines perturbation space around a point.
    Example: L2 ball with epsilon.
    """

    metric: str
    eps: float
    args: dict[str, Any]


@dataclass
class DomainIR:
    """
    Optional domain restriction (categorical, numeric bounds, etc.)
    """

    name: str
    args: dict[str, Any]


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
    """
    Atomic predicate:
        x'.age <= 30

    Represents a leaf condition in the logical tree.

    The dtype fields are optional because IR1 can still exist without
    ModelSchema-aware validation, but when schema validation is enabled,
    they become the bridge toward backend typing.
    """

    entity: str
    feature: str
    op: EnumComparisonOperator
    value: Any

    feature_dtype: EnumDataType | None = None
    value_dtype: EnumDataType | None = None


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
