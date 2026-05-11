from model.errors.base import ModelError


class ModelLoadError(ModelError):
    pass


class UnsupportedFormatError(ModelError):
    pass