from forml.grammar.official_contents.functions import EnumFunction
from forml.grammar.official_contents.properties import EnumProperty
from forml.semantic.scope import SemanticScope


# -------------------------------
# Problem ↔ Function
# -------------------------------
PROBLEM_FUNCTION_COMPATIBILITY = {
    "CLASSIFICATION": {
        EnumFunction.EQUAL,
        EnumFunction.EQUITY,
        EnumFunction.BETWEEN,
    },
    "REGRESSION": {
        EnumFunction.EQUAL,
        EnumFunction.INCREASING,
        EnumFunction.DECREASING,
        EnumFunction.BETWEEN,
    },
    "CLUSTERING": set()
}


# -------------------------------
# Property ↔ Scope (IMPORTANT 🔥)
# -------------------------------
PROPERTY_SCOPE_COMPATIBILITY = {
    "ROBUSTNESS": {
        SemanticScope.GLOBAL,
        SemanticScope.LOCAL,
        SemanticScope.POINTWISE,
    },
    "FAIRNESS": {
        SemanticScope.PAIRWISE,
    },
    "MONOTONICITY": {
        SemanticScope.PAIRWISE,
        SemanticScope.GLOBAL,
    },
    "STABILITY": {
        SemanticScope.LOCAL,
        SemanticScope.GLOBAL,
    },
    "BOUNDS": {
        SemanticScope.POINTWISE,
        SemanticScope.GLOBAL,
    },
}


# -------------------------------
# Property ↔ Backend
# -------------------------------
PROPERTY_MODEL_COMPATIBILITY = {
    "ONNX": {"ROBUSTNESS", "STABILITY", "FAIRNESS"},
    "SKLEARN": {"FAIRNESS", "BOUNDS"},
    "PYTORCH": {"ROBUSTNESS", "MONOTONICITY", "STABILITY"},
}