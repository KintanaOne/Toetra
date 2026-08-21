from __future__ import annotations

from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.ir_builder.registry import ModelIRBuilderRegistry
from toetra._models.ir_builder.sklearn_affine import SklearnAffineModelIRBuilder


def create_default_model_ir_builder_registry() -> ModelIRBuilderRegistry:
    registry = ModelIRBuilderRegistry()
    builder = SklearnAffineModelIRBuilder()
    for model_type in ("LinearRegression", "LogisticRegression"):
        registry.register(EnumModelFramework.SKLEARN, model_type, builder)
    return registry
