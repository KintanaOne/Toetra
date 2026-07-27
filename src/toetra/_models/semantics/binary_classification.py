from __future__ import annotations

from toetra._compiler.ir.ir1.nodes import VerificationTask
from toetra._models.families import (
    BINARY_LOGISTIC_AFFINE_MODEL_FAMILY,
    BINARY_LOGISTIC_AFFINE_SEMANTIC_PROFILE_ID,
)
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.semantics.base import LoweredVerificationTask
from toetra._models.semantics.binary_classification_common import (
    BinaryClassificationLoweringProfile,
)
from toetra._models.semantics.binary_classification_lowering import (
    lower_binary_classification_task,
)

__all__ = [
    "BINARY_LOGISTIC_AFFINE_MODEL_FAMILY",
    "BinaryLogisticAffineClassificationProfile",
]


class BinaryLogisticAffineClassificationProfile:
    """Initial binary classification semantics independent from implementation."""

    profile_id = BINARY_LOGISTIC_AFFINE_SEMANTIC_PROFILE_ID
    version = "1"
    label_transformation_id = "predicted_label_literal_to_oriented_decision_value"
    probability_transformation_id = (
        "class_probability_threshold_to_oriented_decision_value"
    )
    label_transformation_version = "1"
    probability_transformation_version = "2"

    def lower_task(
        self,
        task: VerificationTask,
        *,
        schema: ModelSchema,
    ) -> LoweredVerificationTask:
        profile = BinaryClassificationLoweringProfile(
            profile_id=self.profile_id,
            version=self.version,
            label_transformation_id=self.label_transformation_id,
            probability_transformation_id=self.probability_transformation_id,
            label_transformation_version=self.label_transformation_version,
            probability_transformation_version=self.probability_transformation_version,
        )
        return lower_binary_classification_task(
            task,
            schema=schema,
            profile=profile,
        )
