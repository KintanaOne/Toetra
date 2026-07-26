from __future__ import annotations

from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.encoder.registry import ModelEncoderRegistry
from toetra._models.encoder.sklearn.linear import SklearnLinearRegressorEncoder
from toetra._models.encoder.sklearn.logistic import SklearnLogisticRegressionEncoder


def create_default_model_encoder_registry() -> ModelEncoderRegistry:
    """Create the default registry of built-in backend-independent encoders."""

    registry = ModelEncoderRegistry()
    registry.register(
        EnumModelFramework.SKLEARN,
        SklearnLinearRegressorEncoder(),
        model_type="LinearRegression",
    )
    registry.register(
        EnumModelFramework.SKLEARN,
        SklearnLogisticRegressionEncoder(),
        model_type="LogisticRegression",
    )
    return registry
