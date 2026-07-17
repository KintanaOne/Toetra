"""Derived compatibility labels for point-aware semantic contexts.

`SemanticScope` is not the semantic source of truth. Point bindings, lexical
frames, restrictions, and model evaluations live in `PointEnvironment` and
semantic annotations. These labels remain only for older reports and consumers.
"""

from enum import Enum


class SemanticScope(Enum):
    QUANTIFIER = "quantifier"
    LOCAL = "local"
    POINTWISE = "pointwise"
    PAIRWISE = "pairwise"


def get_scope_from_property(prop):
    """Return a legacy source-shape classification.

    New semantic code must not use this helper to decide binding, visibility,
    property compatibility, or backend capability.
    """
    if prop.pairwise_expr:
        return SemanticScope.PAIRWISE

    if prop.anchor_expr:
        if prop.anchor_expr.anchor == "check_at":
            return SemanticScope.POINTWISE
        return SemanticScope.LOCAL

    if prop.quantifier_expr:
        return SemanticScope.QUANTIFIER

    return None
