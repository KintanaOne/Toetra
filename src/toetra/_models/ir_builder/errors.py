from __future__ import annotations

from toetra._models.errors.base import ModelError


class ModelIRBuilderError(ModelError):
    """Base error for source-model to Model IR construction."""


class UnsupportedModelIRBuilderError(ModelIRBuilderError):
    """Raised when no Model IR builder supports a normalized model schema."""


class MissingModelIRParameterError(ModelIRBuilderError):
    """Raised when compatibility construction lacks required model parameters."""


class InvalidModelIRParameterError(ModelIRBuilderError):
    """Raised when source parameters cannot define a valid Model IR."""
