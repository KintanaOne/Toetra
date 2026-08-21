from __future__ import annotations


class ModelIRLoweringError(Exception):
    """Base error for compiler-owned Model IR lowering."""


class UnsupportedModelIRLoweringError(ModelIRLoweringError):
    """Raised when no compiler lowerer supports a Model IR/schema pair."""


class InvalidModelIRLoweringError(ModelIRLoweringError):
    """Raised when lowering cannot emit valid evaluation-specific IR2."""
