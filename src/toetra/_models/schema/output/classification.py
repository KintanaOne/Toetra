from dataclasses import dataclass
import math

from toetra._models.schema.output.base import ModelOutputSchema
from toetra._models.schema.output.decision_policy import (
    BinaryClassificationDecisionPolicy,
    ModelLabel,
)
from toetra._models.schema.output.enums import (
    EnumModelOutputKind,
    EnumOutputObservable,
)


@dataclass(frozen=True)
class ClassificationOutputSchema(ModelOutputSchema):
    """Typed classification output and its observable capabilities."""

    labels: tuple[ModelLabel, ...] = ()
    probability_available: bool = False
    decision_policy: BinaryClassificationDecisionPolicy | None = None

    def __post_init__(self) -> None:
        super().__post_init__()

        if not isinstance(self.labels, tuple):
            raise TypeError("ClassificationOutputSchema labels must be a tuple.")

        for label in self.labels:
            if not isinstance(label, (str, int, float, bool)):
                raise TypeError(
                    "Classification labels must be JSON-compatible scalar values."
                )

            if isinstance(label, float) and not math.isfinite(label):
                raise ValueError("Classification labels must be finite.")

        if len(set(self.labels)) != len(self.labels):
            raise ValueError("Classification output labels must be unique.")

        if not isinstance(self.probability_available, bool):
            raise TypeError(
                "ClassificationOutputSchema probability_available must be a bool."
            )

        if self.decision_policy is not None and not isinstance(
            self.decision_policy,
            BinaryClassificationDecisionPolicy,
        ):
            raise TypeError(
                "ClassificationOutputSchema decision_policy must be a "
                "BinaryClassificationDecisionPolicy or None."
            )

        if self.decision_policy is None:
            return

        if len(self.labels) != 2:
            raise ValueError(
                "A binary decision policy requires exactly two output labels."
            )

        expected = (
            self.decision_policy.negative_label,
            self.decision_policy.positive_label,
        )

        if self.labels != expected:
            raise ValueError(
                "Classification labels must preserve the decision policy's "
                "negative/positive orientation."
            )

        if not self.probability_available:
            raise ValueError(
                "A binary decision policy requires probability observability."
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
