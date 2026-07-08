from __future__ import annotations

from model.detector.model_framework import EnumModelFramework
from model.encoder.registry import ModelEncoderRegistry
from model.encoder.sklearn.linear import SklearnLinearRegressorEncoder


def create_default_model_encoder_registry() -> ModelEncoderRegistry:
    """Create the default registry of built-in backend-independent encoders."""

    registry = ModelEncoderRegistry()
    registry.register(
        EnumModelFramework.SKLEARN,
        SklearnLinearRegressorEncoder(),
        model_type="LinearRegression",
    )
    return registry
