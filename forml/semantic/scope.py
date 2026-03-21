# forml/semantic/scope.py

from enum import Enum

class SemanticScope(Enum):
    GLOBAL = "global"
    LOCAL = "local"
    POINTWISE = "pointwise"
    PAIRWISE = "pairwise"

def get_scope_from_property(prop):
    if prop.pairwise_expr:
        return SemanticScope.PAIRWISE
    
    if prop.anchor_expr:
        # check_at vs at
        if prop.anchor_expr.anchor == "check_at":
            return SemanticScope.POINTWISE
        return SemanticScope.LOCAL

    if prop.universal_expr:
        return SemanticScope.GLOBAL

    return None