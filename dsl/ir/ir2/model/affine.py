from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dsl.ir.ir2.model.base import ModelConstraintIR2
from dsl.language.vocabulary.operators import EnumComparisonOperator


@dataclass(frozen=True)
class AffineTermIR2:
    """One term of an affine model expression: coefficient * entity.feature."""

    entity: str
    feature: str
    coefficient: float


@dataclass
class AffineExpressionIR2:
    """Backend-neutral affine expression used by simple model encoders.

    Example:
        0.5 * x.a + -1.2 * x.b + 3.0
    """

    terms: tuple[AffineTermIR2, ...]
    bias: float = 0.0


@dataclass
class AffineOutputConstraintIR2(ModelConstraintIR2):
    """Atomic affine model assumption relating output to w·x + b.

    This is intentionally backend-independent. It does not encode Z3 terms and
    does not decide the final normal form. It only states a model-level fact
    that can participate in Γ before IR2 builds Γ ∧ ¬P.
    """

    output_entity: str
    output_feature: str
    op: EnumComparisonOperator
    expression: AffineExpressionIR2
    metadata: dict[str, Any] = field(default_factory=dict)
