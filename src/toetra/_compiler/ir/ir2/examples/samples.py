from __future__ import annotations

DEFAULT_SAMPLE = """
model := "model.onnx"
target := MyTarget

[LOGIC]:
forall x0 => a <= 1 -> b <= 2 using Z3
"""

REAL_LINEAR_MODEL_SAMPLE = """
model := "model.joblib"
target := MyTarget

[BOUND]:
forall x0 => target <= 10 using Z3
"""
