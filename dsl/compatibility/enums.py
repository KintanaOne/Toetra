from __future__ import annotations

from enum import Enum


class SupportStatus(str, Enum):
    """Implementation status of one framework/model/backend route."""

    SUPPORTED = "supported"
    EXPERIMENTAL = "experimental"
    PLANNED = "planned"
    UNSUPPORTED = "unsupported"


class CompatibilityClassification(str, Enum):
    """Semantic relationship between source and encoded behaviors."""

    EXACT = "exact"
    SOUND_OVER_APPROXIMATION = "sound_over_approximation"
    SOUND_UNDER_APPROXIMATION = "sound_under_approximation"
    LOSSY = "lossy"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"


class BackendKind(str, Enum):
    """Backend family independent from a concrete implementation."""

    SMT = "smt"
    MILP = "milp"
    INTERVAL_ANALYSIS = "interval_analysis"
    ABSTRACT_INTERPRETATION = "abstract_interpretation"
    SYMBOLIC_ALGEBRA = "symbolic_algebra"
    CONCRETE_RUNTIME_SEARCH = "concrete_runtime_search"
    REMOTE_VERIFICATION_SERVICE = "remote_verification_service"
    UNKNOWN = "unknown"


class NumericFamily(str, Enum):
    INTEGER = "integer"
    RATIONAL = "rational"
    DECIMAL = "decimal"
    BINARY_FLOAT = "binary_float"
    REAL = "real"
    INTERVAL = "interval"
    BITVECTOR = "bitvector"
    UNKNOWN = "unknown"


class NumericRounding(str, Enum):
    EXACT = "exact"
    NEAREST_EVEN = "nearest_even"
    TOWARD_ZERO = "toward_zero"
    DIRECTED = "directed"
    BACKEND_DEFINED = "backend_defined"
    UNKNOWN = "unknown"


class SpecialValuePolicy(str, Enum):
    SUPPORTED = "supported"
    REJECTED = "rejected"
    UNKNOWN = "unknown"


class RangeBehavior(str, Enum):
    UNBOUNDED = "unbounded"
    FINITE_IEEE754 = "finite_ieee754"
    SATURATING = "saturating"
    WRAPPING = "wrapping"
    UNKNOWN = "unknown"


class ConclusionKind(str, Enum):
    UNIVERSAL_PROOF = "universal_proof"
    UNIVERSAL_COUNTEREXAMPLE = "universal_counterexample"
    EXISTENTIAL_WITNESS = "existential_witness"
    EXISTENTIAL_NO_WITNESS = "existential_no_witness"


class ConclusionScope(str, Enum):
    SOURCE_ARTIFACT = "source_artifact"
    SEMANTIC_TARGET_ONLY = "semantic_target_only"
