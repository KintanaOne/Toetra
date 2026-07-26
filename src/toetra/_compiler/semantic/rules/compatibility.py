# src/toetra/_compiler/semantic/rules/compatibility.py

from toetra._language.vocabulary.functions import EnumFunction
from toetra._language.vocabulary.problems import EnumProblem
from toetra._language.vocabulary.properties import EnumProperty

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
# Property ↔ Point environment
# -------------------------------


def validate_property_point_contract(property_type, context) -> None:
    """Validate property-specific point requirements without scope enums.

    Point binding, target resolution and restrictions are already validated by
    the composed semantic environment.  Property labels therefore do not gate
    mutually exclusive ``POINTWISE``/``LOCAL``/``PAIRWISE`` categories.  The
    only V1 structural rule retained here is that FAIRNESS is relational and
    requires at least two visible points.
    """

    if property_type is EnumProperty.FAIRNESS:
        point_count = len(context.point_environment.all())
        if point_count < 2:
            from toetra._compiler.semantic.errors.errors import InvalidPropertyError

            raise InvalidPropertyError(
                "Property 'FAIRNESS' requires at least two visible points"
            )


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
