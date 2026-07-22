from __future__ import annotations


class ModelSemanticLoweringError(Exception):
    """Base error for model-family semantic lowering."""


class MissingModelSemanticsError(ModelSemanticLoweringError):
    """Raised when an observable requires a model semantic profile."""


class UnsupportedModelSemanticProfileError(ModelSemanticLoweringError):
    """Raised when no registered semantic profile matches the model schema."""


class UnsupportedObservableLoweringError(ModelSemanticLoweringError):
    """Raised when a profile does not define the requested observable rewrite."""


class InvalidModelSemanticProfileError(ModelSemanticLoweringError):
    """Raised when a schema violates the selected semantic profile contract."""
