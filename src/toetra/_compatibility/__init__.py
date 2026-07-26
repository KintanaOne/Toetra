"""Framework/src/toetra/_models/encoder/backend numeric compatibility contracts."""

from toetra._compatibility.defaults import (
    SKLEARN_AFFINE_TO_EXACT_REAL_RULE_ID,
    SKLEARN_BINARY_LOGISTIC_EXACT_PROBABILITY_RULE_ID,
    SKLEARN_BINARY_LOGISTIC_PROBABILITY_RULE_ID,
    SKLEARN_BINARY_LOGISTIC_TO_EXACT_REAL_RULE_ID,
    create_default_numeric_compatibility_registry,
)
from toetra._compatibility.descriptors import (
    BackendProfileDescriptor,
    FrameworkModelDescriptor,
    ModelEncoderDescriptor,
    NumericSemanticDescriptor,
    PropertyNumericRequirements,
)
from toetra._compatibility.enums import (
    BackendKind,
    CompatibilityClassification,
    ConclusionKind,
    ConclusionScope,
    NumericFamily,
    NumericRounding,
    RangeBehavior,
    SpecialValuePolicy,
    SupportStatus,
)
from toetra._compatibility.errors import (
    AmbiguousCompatibilityRuleError,
    DuplicateCompatibilityRuleError,
    InvalidCompatibilityDescriptorError,
    InvalidCompatibilityRuleError,
    NumericCompatibilityError,
)
from toetra._compatibility.matrix import (
    CompatibilityMatrixRow,
    compatibility_matrix_rows,
    render_compatibility_matrices_markdown,
    write_compatibility_matrices_markdown,
)
from toetra._compatibility.model import (
    CompatibilityRule,
    CompatibilityRulePattern,
    NumericCompatibilityAssessment,
    NumericCompatibilityContext,
    NumericCompatibilityQuery,
)
from toetra._compatibility.policy import (
    apply_numeric_compatibility_policy,
    apply_semantic_lowering_policy,
)
from toetra._compatibility.registry import NumericCompatibilityRegistry

__all__ = [
    "AmbiguousCompatibilityRuleError",
    "BackendKind",
    "BackendProfileDescriptor",
    "CompatibilityClassification",
    "CompatibilityMatrixRow",
    "CompatibilityRule",
    "CompatibilityRulePattern",
    "ConclusionKind",
    "ConclusionScope",
    "DuplicateCompatibilityRuleError",
    "FrameworkModelDescriptor",
    "InvalidCompatibilityDescriptorError",
    "InvalidCompatibilityRuleError",
    "ModelEncoderDescriptor",
    "NumericCompatibilityAssessment",
    "NumericCompatibilityContext",
    "NumericCompatibilityError",
    "NumericCompatibilityQuery",
    "NumericCompatibilityRegistry",
    "NumericFamily",
    "NumericRounding",
    "NumericSemanticDescriptor",
    "PropertyNumericRequirements",
    "RangeBehavior",
    "SKLEARN_AFFINE_TO_EXACT_REAL_RULE_ID",
    "SKLEARN_BINARY_LOGISTIC_EXACT_PROBABILITY_RULE_ID",
    "SKLEARN_BINARY_LOGISTIC_PROBABILITY_RULE_ID",
    "SKLEARN_BINARY_LOGISTIC_TO_EXACT_REAL_RULE_ID",
    "SpecialValuePolicy",
    "SupportStatus",
    "apply_numeric_compatibility_policy",
    "apply_semantic_lowering_policy",
    "write_compatibility_matrices_markdown",
    "render_compatibility_matrices_markdown",
    "compatibility_matrix_rows",
    "create_default_numeric_compatibility_registry",
]
