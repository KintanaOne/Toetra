from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from toetra._compiler.ir.ir1.model_quantities import ModelQuantityExpressionIR
from toetra._compiler.ir.ir1.nodes import ModelEvaluationIR, PointBindingIR
from toetra._compiler.ir.ir2.model.base import ModelConstraintIR2
from toetra._language.vocabulary.operators import EnumComparisonOperator


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


@dataclass
class AffineModelQuantityConstraintIR2(ModelConstraintIR2):
    """Affine equation defining one internal model-semantic quantity."""

    quantity: ModelQuantityExpressionIR
    op: EnumComparisonOperator
    expression: AffineExpressionIR2
    evaluation: ModelEvaluationIR | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.evaluation is None:
            self.evaluation = self.quantity.evaluation
        elif self.evaluation != self.quantity.evaluation:
            raise ValueError(
                "Affine model quantity and constraint evaluation must match"
            )

    @property
    def point(self) -> PointBindingIR:
        return self.quantity.point

    @property
    def model_identity(self) -> str:
        return self.quantity.model_identity
