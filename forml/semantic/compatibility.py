# forml/semantic/compatibility.py

from forml.language.vocabulary.functions import EnumFunction
from forml.language.vocabulary.properties import EnumProperty
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
        SemanticScope.QUANTIFIER,
        SemanticScope.LOCAL,
        SemanticScope.POINTWISE,
    },
    "FAIRNESS": {
        SemanticScope.PAIRWISE,
    },
    "MONOTONICITY": {
        SemanticScope.PAIRWISE,
        SemanticScope.QUANTIFIER,
    },
    "STABILITY": {
        SemanticScope.LOCAL,
        SemanticScope.QUANTIFIER,
    },
    "BOUNDS": {
        SemanticScope.POINTWISE,
        SemanticScope.QUANTIFIER,
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