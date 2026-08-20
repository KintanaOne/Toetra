# src/toetra/_models/ir/affine.py

import math
from dataclasses import dataclass
from typing import TypeAlias

from toetra._models.ir.base import ModelIR

AffineTerm: TypeAlias = tuple[str, float]


@dataclass(frozen=True, slots=True)
class AffineModelIR(ModelIR):
    """Normalized Toetra affine model representation.

    This is the internal representation of an affine model in Toetra.
    """

    terms: tuple[AffineTerm, ...]
    bias: float

    def __post_init__(self) -> None:
        if not isinstance(self.terms, tuple):
            raise TypeError("Terms must be a tuple of (feature, coefficient) pairs.")

        seen: set[str] = set()
        for affine_term in self.terms:
            if not isinstance(affine_term, tuple):
                raise TypeError("Each term must be a tuple of (feature, coefficient).")
            if len(affine_term) != 2:
                raise ValueError(
                    "Each term must have exactly two elements: "
                    "(feature, coefficient)."
                )
            feature, coefficient = affine_term

            if not isinstance(feature, str):
                raise TypeError("Feature name must be a string.")
            if not feature:
                raise ValueError("Feature name cannot be empty.")
            if feature.strip() != feature:
                raise ValueError(
                    "Feature name cannot have leading or trailing whitespace."
                )
            if feature in seen:
                raise ValueError(f"Duplicate feature name detected: {feature}")
            seen.add(feature)

            if type(coefficient) is not float:
                raise TypeError("Coefficient must be a float value.")
            if not math.isfinite(coefficient):
                raise ValueError("Coefficient must be a finite float value.")

        if type(self.bias) is not float:
            raise TypeError("Bias must be a float value.")
        if not math.isfinite(self.bias):
            raise ValueError("Bias must be a finite float value.")
