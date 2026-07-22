from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from dsl.ir.ir1.nodes import ModelEvaluationIR, PointBindingIR, ScalarExpressionIR
from dsl.semantic.types.enums import EnumDataType


class EnumModelQuantityKind(str, Enum):
    """Backend-neutral quantities introduced by model semantic lowering."""

    ORIENTED_DECISION_VALUE = "oriented_decision_value"


@dataclass
class ModelQuantityExpressionIR(ScalarExpressionIR):
    """Internal mathematical quantity attached to one model evaluation.

    This node is never a public DSL observable. It exists only after a
    model-family semantic profile has lowered a declarative output intent.
    """

    evaluation: ModelEvaluationIR
    quantity_kind: EnumModelQuantityKind
    semantic_profile_id: str
    dtype: EnumDataType = EnumDataType.FLOAT

    @property
    def point(self) -> PointBindingIR:
        return self.evaluation.point

    @property
    def model_identity(self) -> str:
        return self.evaluation.model_identity

    @property
    def output_name(self) -> str:
        return self.evaluation.output_name
