from __future__ import annotations


class ModelEncoderError(Exception):
    """Base error for model assumption encoding."""


class UnsupportedModelEncoderError(ModelEncoderError):
    """Raised when no encoder is registered for a model schema."""


class InvalidModelAssumptionError(ModelEncoderError):
    """Raised when an encoder emits invalid IR2 assumptions."""


class MissingModelParameterError(ModelEncoderError):
    """Raised when a schema does not expose parameters required by an encoder."""


class UnsupportedModelParameterError(ModelEncoderError):
    """Raised when model parameters are present but outside the encoder scope."""
