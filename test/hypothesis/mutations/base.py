from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable


class MutationNature(Enum):
    STRUCTURAL = auto()
    SEMANTIC = auto()
    LOGICAL = auto()
    NUMERICAL = auto()
    ADVERSARIAL = auto()
    CATEGORICAL = auto()
    STOCHASTIC = auto()


class MutationImpact(Enum):
    NONE = auto()
    PARSING = auto()
    AST_INVALID = auto()
    SEMANTIC_INVALID = auto()
    TYPE_INVALID = auto()
    EXECUTION_FAILURE = auto()


class MutationSeverity(Enum):
    INFO = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()
    CATASTROPHIC = auto()


class PipelineStage(Enum):
    PARSING = auto()
    AST_BUILDING = auto()
    SEMANTIC_ANALYSIS = auto()
    TYPE_CHECKING = auto()
    TRANSFORMATION = auto()
    EXECUTION = auto()


@dataclass(frozen=True)
class MutationMetadata:
    """
    Metadata describing a mutation strategy.

    This metadata is used to:
    - classify mutations
    - orchestrate mutation campaigns
    - measure robustness per pipeline stage
    - define expected failure locations
    - support future reporting / analytics
    """

    name: str

    nature: MutationNature
    severity: MutationSeverity
    severity_score: float

    impact: set[MutationImpact]

    expected_failures: set[PipelineStage]

    preserves_valid_ast: bool
    preserves_typing: bool
    deterministic: bool = True

    preserves_semantic_equivalence: bool = False


def mutation(
    *,
    nature: MutationNature,
    severity: MutationSeverity,
    severity_score: float,
    impact: set[MutationImpact],
    expected_failures: set[PipelineStage],
    preserves_valid_ast: bool,
    preserves_typing: bool,
    deterministic: bool = True,
    preserves_semantic_equivalence: bool = False,
):
    """
    Attach metadata directly to mutation functions.
    """

    def decorator(func: Callable):

        func.metadata = MutationMetadata(
            name=func.__name__,
            nature=nature,
            severity=severity,
            severity_score=severity_score,
            impact=impact,
            expected_failures=expected_failures,
            preserves_valid_ast=preserves_valid_ast,
            preserves_typing=preserves_typing,
            deterministic=deterministic,
        )

        return func

    return decorator
