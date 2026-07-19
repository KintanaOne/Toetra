"""Framework/model/encoder/backend numeric compatibility contracts."""

from dsl.compatibility.defaults import (
    SKLEARN_AFFINE_TO_EXACT_REAL_RULE_ID,
    create_default_numeric_compatibility_registry,
)
from dsl.compatibility.descriptors import (
    BackendProfileDescriptor,
    FrameworkModelDescriptor,
    ModelEncoderDescriptor,
    NumericSemanticDescriptor,
    PropertyNumericRequirements,
)
from dsl.compatibility.enums import (
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
from dsl.compatibility.errors import (
    AmbiguousCompatibilityRuleError,
    DuplicateCompatibilityRuleError,
    InvalidCompatibilityDescriptorError,
    InvalidCompatibilityRuleError,
    NumericCompatibilityError,
)
from dsl.compatibility.matrix import (
    CompatibilityMatrixRow,
    compatibility_matrix_rows,
    render_compatibility_matrices_markdown,
    write_compatibility_matrices_markdown,
)
from dsl.compatibility.model import (
    CompatibilityRule,
    CompatibilityRulePattern,
    NumericCompatibilityAssessment,
    NumericCompatibilityContext,
    NumericCompatibilityQuery,
)
from dsl.compatibility.policy import apply_numeric_compatibility_policy
from dsl.compatibility.registry import NumericCompatibilityRegistry

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
    "SpecialValuePolicy",
    "SupportStatus",
    "apply_numeric_compatibility_policy",
    "write_compatibility_matrices_markdown",
    "render_compatibility_matrices_markdown",
    "compatibility_matrix_rows",
    "create_default_numeric_compatibility_registry",
]
