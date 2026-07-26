CHECK_AT_INCOME = """
model := "model.onnx"
target := MyTarget

[ROBUSTNESS]:
forall x0 => x0.income <= 1000
"""

CHECK_AT_IMPLICIT_AGE = """
model := "model.onnx"
target := MyTarget

[ROBUSTNESS]:
forall x0 => age <= 30
"""

FORALL_IMPLICIT_AGE = """
model := "model.onnx"
target := MyTarget

[ROBUSTNESS]:
forall x0 => age <= 30
"""

CHECK_AT_BOOL_FEATURE = """
model := "model.onnx"
target := MyTarget

[ROBUSTNESS]:
forall x0 => x0.is_active == true
"""

NESTED_TYPED_LOGIC = """
model := "model.onnx"
target := MyTarget

[ROBUSTNESS]:
forall x0 => (x0.age <= 30 OR x0.income >= 1000) AND x0.is_active == true
"""


CLASSIFICATION_OBSERVABLES = """
model := "credit.joblib"
target := decision

[LOGIC]:
forall applicant =>
    target[applicant].label == "approved"
    and target[applicant].probability("approved") >= 0.80
"""
