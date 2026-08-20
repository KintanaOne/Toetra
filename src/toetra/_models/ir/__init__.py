"""Framework- and backend-agnostic model computation representations."""

from toetra._models.ir.affine import AffineModelIR, AffineTerm
from toetra._models.ir.base import ModelIR

__all__ = ["AffineModelIR", "AffineTerm", "ModelIR"]
