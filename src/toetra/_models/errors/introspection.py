from toetra._models.errors.base import ModelError


class ModelIntrospectionError(ModelError):
    pass


class MissingFeatureMetadataError(ModelIntrospectionError):
    pass


class ReferenceDatasetError(ModelIntrospectionError):
    """Raised when the reference dataset cannot be read as a CSV artifact."""


class UnsupportedIntrospectorError(ModelIntrospectionError):
    pass
