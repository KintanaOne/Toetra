from dataclasses import dataclass
from decimal import Decimal
import math
from typing import TypeAlias

from toetra._models.families import (
    BINARY_LOGISTIC_AFFINE_SEMANTIC_PROFILE_ID,
)

ModelLabel: TypeAlias = str | int | float | bool


def _validate_label(label: ModelLabel, *, field_name: str) -> None:
    if not isinstance(label, (str, int, float, bool)):
        raise TypeError(f"{field_name} must be a string, integer, float, or boolean.")

    if isinstance(label, float) and not math.isfinite(label):
        raise ValueError(f"{field_name} must be finite.")


@dataclass(frozen=True)
class BinaryClassificationDecisionPolicy:
    """Framework-neutral decision policy for a binary classifier."""

    negative_label: ModelLabel
    positive_label: ModelLabel
    probability_threshold: Decimal = Decimal("0.5")
    oriented_decision_threshold: Decimal = Decimal("0")
    positive_when_strictly_greater: bool = True
    policy_source: str = "recognized_model_profile"
    semantic_profile_id: str = BINARY_LOGISTIC_AFFINE_SEMANTIC_PROFILE_ID

    def __post_init__(self) -> None:
        _validate_label(self.negative_label, field_name="negative_label")
        _validate_label(self.positive_label, field_name="positive_label")

        if self.negative_label == self.positive_label:
            raise ValueError("Binary decision policy labels must be distinct.")

        if not isinstance(self.probability_threshold, Decimal):
            raise TypeError("Probability threshold must be a Decimal.")

        if not self.probability_threshold.is_finite():
            raise ValueError("Probability threshold must be finite.")

        if not Decimal("0") <= self.probability_threshold <= Decimal("1"):
            raise ValueError("Probability threshold must be between 0 and 1.")

        if not isinstance(self.oriented_decision_threshold, Decimal):
            raise TypeError("Oriented decision threshold must be a Decimal.")

        if not self.oriented_decision_threshold.is_finite():
            raise ValueError("Oriented decision threshold must be finite.")

        if not isinstance(self.positive_when_strictly_greater, bool):
            raise TypeError("positive_when_strictly_greater must be a bool.")

        if not isinstance(self.policy_source, str):
            raise TypeError("Decision policy source must be a string.")

        if not self.policy_source:
            raise ValueError("Decision policy source cannot be empty.")

        if self.policy_source.strip() != self.policy_source:
            raise ValueError(
                "Decision policy source cannot have leading or trailing whitespace."
            )

        if not isinstance(self.semantic_profile_id, str):
            raise TypeError("Semantic profile identifier must be a string.")

        if not self.semantic_profile_id:
            raise ValueError("Semantic profile identifier cannot be empty.")

        if self.semantic_profile_id.strip() != self.semantic_profile_id:
            raise ValueError(
                "Semantic profile identifier cannot have leading or "
                "trailing whitespace."
            )

    @property
    def equality_label(self) -> ModelLabel:
        """Return the label selected exactly on the native boundary."""

        if self.positive_when_strictly_greater:
            return self.negative_label

        return self.positive_label
