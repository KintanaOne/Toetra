from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dsl.ir.ir1.nodes import ModelEvaluationIR, PointBindingIR
from dsl.ir.ir2.model.base import ModelConstraintIR2
from dsl.language.vocabulary.operators import EnumComparisonOperator


@dataclass(frozen=True)
class AffineTermIR2:
    """One term of an affine model expression: coefficient * point.feature."""

    entity: str
    feature: str
    coefficient: float
    point: PointBindingIR | None = None


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
    """Atomic affine model equation for one explicit model evaluation."""

    output_entity: str
    output_feature: str
    op: EnumComparisonOperator
    expression: AffineExpressionIR2
    evaluation: ModelEvaluationIR | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def point(self) -> PointBindingIR | None:
        """Return the input point attached to the structured evaluation."""
        return self.evaluation.point if self.evaluation is not None else None

    @property
    def model_identity(self) -> str | None:
        """Return the declared model identity for this equation."""
        return self.evaluation.model_identity if self.evaluation is not None else None
