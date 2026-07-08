from __future__ import annotations


class ModelEncoderError(Exception):
    """Base error for model assumption encoding."""


class UnsupportedModelEncoderError(ModelEncoderError):
    """Raised when no encoder is registered for a model schema."""


class InvalidModelAssumptionError(ModelEncoderError):
    """Raised when an encoder emits invalid IR2 assumptions."""
