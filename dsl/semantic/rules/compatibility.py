# forml/semantic/compatibility.py

from dsl.language.vocabulary.functions import EnumFunction
from dsl.language.vocabulary.problems import EnumProblem
from dsl.language.vocabulary.properties import EnumProperty
from dsl.semantic.context.scope import SemanticScope

# -------------------------------
# Problem ↔ Function
# -------------------------------
PROBLEM_FUNCTION_COMPATIBILITY = {
    EnumProblem.CLASSIFICATION: {
        EnumFunction.EQUAL,
        EnumFunction.EQUITY,
        EnumFunction.BETWEEN,
    },
    EnumProblem.REGRESSION: {
        EnumFunction.EQUAL,
        EnumFunction.INCREASING,
        EnumFunction.DECREASING,
        EnumFunction.BETWEEN,
    },
    EnumProblem.CLUSTERING: set(),
}


# -------------------------------
# Property ↔ Scope (IMPORTANT 🔥)
# -------------------------------
PROPERTY_SCOPE_COMPATIBILITY = {
    EnumProperty.ROBUSTNESS: {
        SemanticScope.QUANTIFIER,
        SemanticScope.LOCAL,
        SemanticScope.POINTWISE,
    },
    EnumProperty.FAIRNESS: {
        SemanticScope.PAIRWISE,
    },
    EnumProperty.MONOTONICITY: {
        SemanticScope.PAIRWISE,
        SemanticScope.QUANTIFIER,
    },
    EnumProperty.STABILITY: {
        SemanticScope.LOCAL,
        SemanticScope.QUANTIFIER,
    },
    EnumProperty.BOUND: {
        SemanticScope.POINTWISE,
        SemanticScope.QUANTIFIER,
    },
}


# -------------------------------
# Property ↔ Backend
# -------------------------------
PROPERTY_MODEL_COMPATIBILITY = {
    "ONNX": {EnumProperty.ROBUSTNESS, EnumProperty.STABILITY, EnumProperty.FAIRNESS},
    "SKLEARN": {EnumProperty.FAIRNESS, EnumProperty.BOUND},
    "PYTORCH": {
        EnumProperty.ROBUSTNESS,
        EnumProperty.MONOTONICITY,
        EnumProperty.STABILITY,
    },
}
