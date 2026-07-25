from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable
from typing import FrozenSet
from typing import TypeAlias
from typing import Any

"""
Base mutation abstractions for Toetra robustness testing.

This module defines:
- mutation classification
- mutation metadata
- mutation execution contracts
- pipeline failure expectations

The goal is to provide a unified framework for:
- lexical mutations
- structural mutations
- semantic mutations
- logical mutations
- adversarial mutations
- future robustness campaigns

This metadata system enables:
- intelligent mutation orchestration
- robustness benchmarking
- pipeline fault localization
- mutation reporting
- deterministic replay
- future analytics / dashboards
"""


# ============================================================================
# MUTATION LAYERS
# ============================================================================
# Describes WHICH pipeline layer is targeted.
# ============================================================================


class MutationLayer(Enum):
    """
    Pipeline layer targeted by the mutation.
    """

    LEXICAL = auto()
    STRUCTURAL = auto()
    SEMANTIC = auto()
    LOGICAL = auto()
    NUMERICAL = auto()
    ADVERSARIAL = auto()
    CATEGORICAL = auto()
    STOCHASTIC = auto()


# ============================================================================
# MUTATION NATURE
# ============================================================================
# Describes HOW the mutation modifies the artifact.
# ============================================================================


class MutationNature(Enum):
    """
    Conceptual type of transformation applied by the mutation.
    """

    INSERTION = auto()
    DELETION = auto()
    SUBSTITUTION = auto()
    REORDERING = auto()
    CORRUPTION = auto()
    PERTURBATION = auto()
    DUPLICATION = auto()
    TRUNCATION = auto()


# ============================================================================
# MUTATION IMPACT
# ============================================================================
# Describes the expected consequence of a mutation.
# ============================================================================


class MutationImpact(Enum):
    """
    Expected impact caused by the mutation.
    """

    NONE = auto()

    PARSING_FAILURE = auto()
    CST_INVALID = auto()
    AST_INVALID = auto()

    SEMANTIC_INVALID = auto()
    TYPE_INVALID = auto()

    EXECUTION_FAILURE = auto()

    NON_DETERMINISM = auto()
    PERFORMANCE_DEGRADATION = auto()


# ============================================================================
# PIPELINE STAGES
# ============================================================================
# Describes where failures are expected to happen.
# ============================================================================


class PipelineStage(Enum):
    """
    Toetra pipeline execution stages.
    """

    LEXING = auto()

    PARSING = auto()

    CST_VALIDATION = auto()

    AST_BUILDING = auto()

    SEMANTIC_ANALYSIS = auto()

    TYPE_CHECKING = auto()

    TRANSFORMATION = auto()

    EXECUTION = auto()


# ============================================================================
# MUTATION SEVERITY
# ============================================================================
# Describes mutation criticality.
# ============================================================================


class MutationSeverity(Enum):
    """
    Mutation severity level.
    """

    INFO = auto()

    LOW = auto()

    MEDIUM = auto()

    HIGH = auto()

    CRITICAL = auto()

    CATASTROPHIC = auto()


# ============================================================================
# TYPE ALIASES
# ============================================================================

MutationFunction: TypeAlias = Callable[[Any], Any]


# ============================================================================
# MUTATION METADATA
# ============================================================================
# Immutable metadata attached to mutation functions.
# ============================================================================


@dataclass(frozen=True, slots=True)
class MutationMetadata:
    """
    Immutable metadata describing a mutation strategy.

    This metadata supports:
    - mutation orchestration
    - filtering mutation campaigns
    - reproducibility
    - robustness analysis
    - expected failure localization
    - future reporting systems
    """

    # ----------------------------------------------------------------------
    # General identity
    # ----------------------------------------------------------------------

    name: str

    # ----------------------------------------------------------------------
    # Classification
    # ----------------------------------------------------------------------

    layer: MutationLayer

    nature: MutationNature

    severity: MutationSeverity

    severity_score: float

    # ----------------------------------------------------------------------
    # Expected impact
    # ----------------------------------------------------------------------

    impact: FrozenSet[MutationImpact]

    expected_failures: FrozenSet[PipelineStage]

    # ----------------------------------------------------------------------
    # Mutation guarantees
    # ----------------------------------------------------------------------

    preserves_valid_cst: bool

    preserves_valid_ast: bool

    preserves_typing: bool

    preserves_semantic_equivalence: bool = False

    # ----------------------------------------------------------------------
    # Execution characteristics
    # ----------------------------------------------------------------------

    deterministic: bool = True

    reversible: bool = False


# ============================================================================
# DECORATOR
# ============================================================================
# Attaches metadata directly to mutation functions.
# ============================================================================


def mutation(
    *,
    layer: MutationLayer,
    nature: MutationNature,
    severity: MutationSeverity,
    severity_score: float,
    impact: set[MutationImpact],
    expected_failures: set[PipelineStage],
    preserves_valid_cst: bool,
    preserves_valid_ast: bool,
    preserves_typing: bool,
    deterministic: bool = True,
    reversible: bool = False,
    preserves_semantic_equivalence: bool = False,
):
    """
    Attach immutable metadata to a mutation function.

    Example
    -------
    @mutation(
        layer=MutationLayer.LEXICAL,
        nature=MutationNature.CORRUPTION,
        severity=MutationSeverity.HIGH,
        severity_score=0.8,
        impact={MutationImpact.PARSING_FAILURE},
        expected_failures={PipelineStage.PARSING},
        preserves_valid_cst=False,
        preserves_valid_ast=False,
        preserves_typing=False,
    )
    def break_parenthesis(program: str) -> str:
        ...
    """

    # ----------------------------------------------------------------------
    # Validation
    # ----------------------------------------------------------------------

    if not 0.0 <= severity_score <= 1.0:
        raise ValueError("severity_score must be between 0.0 and 1.0")

    # ----------------------------------------------------------------------
    # Decorator
    # ----------------------------------------------------------------------

    def decorator(func: MutationFunction):

        func.metadata = MutationMetadata(
            name=func.__name__,
            layer=layer,
            nature=nature,
            severity=severity,
            severity_score=severity_score,
            impact=frozenset(impact),
            expected_failures=frozenset(expected_failures),
            preserves_valid_cst=preserves_valid_cst,
            preserves_valid_ast=preserves_valid_ast,
            preserves_typing=preserves_typing,
            preserves_semantic_equivalence=(preserves_semantic_equivalence),
            deterministic=deterministic,
            reversible=reversible,
        )

        return func

    return decorator
