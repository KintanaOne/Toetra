from model.errors.base import ModelError


class ModelIntrospectionError(ModelError):
    pass


class MissingFeatureMetadataError(
    ModelIntrospectionError
):
    pass