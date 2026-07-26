from toetra._models.errors.base import ModelError


class ModelDetectionError(ModelError):
    pass


class UnsupportedModelError(ModelError):
    pass
