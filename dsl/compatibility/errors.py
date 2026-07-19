class NumericCompatibilityError(ValueError):
    """Base error for numeric compatibility contracts."""


class InvalidCompatibilityDescriptorError(NumericCompatibilityError):
    """Raised when a descriptor or normalized identity is malformed."""


class DuplicateCompatibilityRuleError(NumericCompatibilityError):
    """Raised when the same normalized rule pattern is registered twice."""


class AmbiguousCompatibilityRuleError(NumericCompatibilityError):
    """Raised when equally specific matching rules conflict."""


class InvalidCompatibilityRuleError(NumericCompatibilityError):
    """Raised when one rule claims conclusions its classification cannot justify."""
