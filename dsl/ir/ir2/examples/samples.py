from __future__ import annotations

DEFAULT_SAMPLE = """
model := "model.onnx"
target := MyTarget

[LOGIC]:
forall => a <= 1 -> b <= 2 using Z3
"""

REAL_LINEAR_MODEL_SAMPLE = """
model := "demo-linear-regression"
target := MyTarget

[LOGIC]:
check_at x0 => x0.a <= 10 using Z3
"""
