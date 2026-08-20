from enum import Enum


class EnumModelOutputKind(Enum):
    """Framework-neutral shape of one model output."""

    REGRESSION = "regression"
    CLASSIFICATION = "classification"
    UNKNOWN = "unknown"


class EnumOutputObservable(Enum):
    """Public observable kinds exposed by a model output."""

    REGRESSION_VALUE = "regression_value"
    PREDICTED_LABEL = "predicted_label"
    CLASS_PROBABILITY = "class_probability"
