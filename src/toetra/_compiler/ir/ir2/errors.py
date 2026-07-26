from __future__ import annotations


class IR2Error(Exception):
    """Base error for IR2 construction and validation."""


class InvalidIR2InputError(IR2Error):
    """Raised when IR2 receives an invalid upstream artifact."""


class InvalidNormalFormError(IR2Error):
    """Raised when a formula does not satisfy its declared normal form."""


class NormalFormExplosionError(IR2Error):
    """Raised when CNF/DNF distribution would exceed the configured limit."""


class IR2ValidationError(IR2Error):
    """Raised when a VerificationTaskIR2 violates its invariants."""


class UnsupportedIR2FormError(IR2Error):
    """Raised when a form is unsupported by the current IR2 implementation."""
