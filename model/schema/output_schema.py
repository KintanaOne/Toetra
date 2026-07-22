from __future__ import annotations

from dataclasses import dataclass
import math
from enum import Enum
from typing import TypeAlias

from dsl.semantic.types.enums import EnumDataType
from model.families import BINARY_LOGISTIC_AFFINE_SEMANTIC_PROFILE_ID

ModelLabel: TypeAlias = str | int | float | bool


class EnumModelOutputKind(Enum):
    """Framework-neutral task shape exposed by one model output port."""

    REGRESSION = "regression"
    CLASSIFICATION = "classification"
    UNKNOWN = "unknown"


class EnumOutputObservable(Enum):
    """Public observable kinds exposed by a typed model output schema."""

    REGRESSION_VALUE = "regression_value"
    PREDICTED_LABEL = "predicted_label"
    CLASS_PROBABILITY = "class_probability"


@dataclass(frozen=True)
class BinaryClassificationDecisionPolicy:
    """Framework-neutral native decision policy for a binary classifier.

    Thresholds are canonical decimal strings so provenance never pretends that
    they were learned floating-point parameters. The initial logistic profile
    uses exact values ``0.5`` and ``0``.
    """

    negative_label: ModelLabel
    positive_label: ModelLabel
    probability_threshold: str = "0.5"
    oriented_decision_threshold: str = "0"
    positive_when_strictly_greater: bool = True
    policy_source: str = "recognized_model_profile"
    semantic_profile_id: str = BINARY_LOGISTIC_AFFINE_SEMANTIC_PROFILE_ID

    def __post_init__(self) -> None:
        if self.negative_label == self.positive_label:
            raise ValueError("Binary decision policy labels must be distinct")
        if not self.probability_threshold.strip():
            raise ValueError("Probability threshold cannot be empty")
        if not self.oriented_decision_threshold.strip():
            raise ValueError("Decision-value threshold cannot be empty")
        if not self.policy_source.strip():
            raise ValueError("Decision policy source cannot be empty")
        if not self.semantic_profile_id.strip():
            raise ValueError("Semantic profile identifier cannot be empty")

    @property
    def equality_label(self) -> ModelLabel:
        """Return the label selected exactly on the native boundary."""

        return self.negative_label


class ModelOutputSchema:
    """Common read-only contract implemented by typed output schemas."""

    @property
    def kind(self) -> EnumModelOutputKind:
        raise NotImplementedError

    @property
    def available_observables(self) -> tuple[EnumOutputObservable, ...]:
        raise NotImplementedError

    @property
    def primary_dtype(self) -> EnumDataType | None:
        raise NotImplementedError

    @property
    def source_dtype(self) -> str | None:
        raise NotImplementedError


@dataclass(frozen=True)
class RegressionOutputSchema(ModelOutputSchema):
    """One directly observable scalar regression value."""

    value_dtype: EnumDataType | None = None
    value_source_dtype: str | None = None

    @property
    def kind(self) -> EnumModelOutputKind:
        return EnumModelOutputKind.REGRESSION

    @property
    def available_observables(self) -> tuple[EnumOutputObservable, ...]:
        return (EnumOutputObservable.REGRESSION_VALUE,)

    @property
    def primary_dtype(self) -> EnumDataType | None:
        return self.value_dtype

    @property
    def source_dtype(self) -> str | None:
        return self.value_source_dtype


@dataclass(frozen=True)
class ClassificationOutputSchema(ModelOutputSchema):
    """Typed labels and public capabilities of one classification output."""

    label_dtype: EnumDataType | None = None
    labels: tuple[ModelLabel, ...] = ()
    label_source_dtype: str | None = None
    probability_available: bool = False
    decision_policy: BinaryClassificationDecisionPolicy | None = None

    def __post_init__(self) -> None:
        for label in self.labels:
            if not isinstance(label, (str, int, float, bool)):
                raise TypeError(
                    "Classification labels must be JSON-compatible scalar values"
                )
            if isinstance(label, float) and not math.isfinite(label):
                raise ValueError("Classification labels must be finite")

        if len(set(self.labels)) != len(self.labels):
            raise ValueError("Classification output labels must be unique")

        if self.decision_policy is not None:
            if len(self.labels) != 2:
                raise ValueError(
                    "A binary decision policy requires exactly two output labels"
                )
            expected = (
                self.decision_policy.negative_label,
                self.decision_policy.positive_label,
            )
            if self.labels != expected:
                raise ValueError(
                    "Classification labels must preserve the decision policy's "
                    "negative/positive orientation"
                )
            if not self.probability_available:
                raise ValueError(
                    "The initial binary logistic decision policy requires class "
                    "probability observability"
                )

    @property
    def kind(self) -> EnumModelOutputKind:
        return EnumModelOutputKind.CLASSIFICATION

    @property
    def available_observables(self) -> tuple[EnumOutputObservable, ...]:
        observables = [EnumOutputObservable.PREDICTED_LABEL]
        if self.probability_available:
            observables.append(EnumOutputObservable.CLASS_PROBABILITY)
        return tuple(observables)

    @property
    def primary_dtype(self) -> EnumDataType | None:
        return self.label_dtype

    @property
    def source_dtype(self) -> str | None:
        return self.label_source_dtype


@dataclass(frozen=True)
class UnknownOutputSchema(ModelOutputSchema):
    """Compatibility schema for tasks not yet normalized by FORML."""

    value_dtype: EnumDataType | None = None
    value_source_dtype: str | None = None

    @property
    def kind(self) -> EnumModelOutputKind:
        return EnumModelOutputKind.UNKNOWN

    @property
    def available_observables(self) -> tuple[EnumOutputObservable, ...]:
        return ()

    @property
    def primary_dtype(self) -> EnumDataType | None:
        return self.value_dtype

    @property
    def source_dtype(self) -> str | None:
        return self.value_source_dtype
