from toetra._models.encoder.base import (
    ModelEncoder,
    validate_model_assumptions,
    validate_model_evaluation_coverage,
)
from toetra._models.encoder.context import ModelEncodingContext
from toetra._models.encoder.defaults import create_default_model_encoder_registry
from toetra._models.encoder.errors import (
    InvalidModelAssumptionError,
    MissingModelParameterError,
    ModelEncoderError,
    UnsupportedModelEncoderError,
    UnsupportedModelParameterError,
)
from toetra._models.encoder.factory import ModelEncoderFactory
from toetra._models.encoder.profile import model_encoder_descriptor
from toetra._models.encoder.registry import (
    ModelEncoderKey,
    ModelEncoderRegistration,
    ModelEncoderRegistry,
)
from toetra._models.encoder.sklearn import (
    SklearnLinearRegressorEncoder,
    SklearnLogisticRegressionEncoder,
)

__all__ = [
    "InvalidModelAssumptionError",
    "MissingModelParameterError",
    "ModelEncoder",
    "ModelEncoderError",
    "ModelEncoderFactory",
    "ModelEncoderKey",
    "ModelEncoderRegistration",
    "ModelEncoderRegistry",
    "ModelEncodingContext",
    "SklearnLinearRegressorEncoder",
    "SklearnLogisticRegressionEncoder",
    "UnsupportedModelEncoderError",
    "UnsupportedModelParameterError",
    "create_default_model_encoder_registry",
    "validate_model_assumptions",
    "validate_model_evaluation_coverage",
    "model_encoder_descriptor",
]
