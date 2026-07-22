from __future__ import annotations

from model.compatibility import framework_model_descriptor
from model.schema.model_schema import ModelSchema
from model.semantics.base import ModelSemanticProfile
from model.semantics.errors import UnsupportedModelSemanticProfileError


class ModelSemanticRegistry:
    """Resolve semantic profiles from framework-neutral model-family IDs."""

    def __init__(self) -> None:
        self._profiles: dict[str, ModelSemanticProfile] = {}

    def register(self, model_family: str, profile: ModelSemanticProfile) -> None:
        normalized = model_family.strip()
        if not normalized:
            raise ValueError("Model semantic family identifier cannot be empty")
        self._profiles[normalized] = profile

    def resolve(self, schema: ModelSchema) -> ModelSemanticProfile:
        family = framework_model_descriptor(schema).model_family
        profile = self._profiles.get(family)
        if profile is None:
            raise UnsupportedModelSemanticProfileError(
                "No model semantic profile is registered for model family "
                f"{family!r}"
            )
        return profile


def create_default_model_semantic_registry() -> ModelSemanticRegistry:
    from model.semantics.binary_classification import (
        BinaryLogisticAffineClassificationProfile,
    )
    from model.families import (
        BINARY_LOGISTIC_AFFINE_MODEL_FAMILY,
    )

    registry = ModelSemanticRegistry()
    registry.register(
        BINARY_LOGISTIC_AFFINE_MODEL_FAMILY,
        BinaryLogisticAffineClassificationProfile(),
    )
    return registry
