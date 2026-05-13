# errors/loading.py

from model.errors.base import ModelError


class ModelLoadingError(ModelError):
    """Base exception for model loading."""


class UnsupportedModelFormatError(ModelLoadingError):
    """Raised when the model format is unsupported."""


class ModelFileNotFoundError(ModelLoadingError):
    """Raised when the model file cannot be found."""


class ModelDeserializationError(ModelLoadingError):
    """Raised when model deserialization fails."""