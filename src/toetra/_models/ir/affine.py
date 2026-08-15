# src/toetra/_models/ir/affine.py

from dataclasses import dataclass

from toetra._models.ir.base import ModelIR

AffineTerm = tuple[str, float]

@dataclass
class AffineModelIR(ModelIR):
    """Normalized Toetra affine model representation.

    This is the internal representation of an affine model in Toetra.
    """

    terms: tuple[AffineTerm, ...]
    bias: float