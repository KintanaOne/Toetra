from model.errors.base import ModelError


class ModelDetectionError(ModelError):
    pass


class UnsupportedModelError(ModelError):
    pass