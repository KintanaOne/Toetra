from __future__ import annotations

import pytest

from toetra._compiler.ir.ir1.run_ir1 import run_ir
from toetra._compiler.semantic.errors.errors import SemanticError
from tests.support.semantic_restrictions import numeric_schema

_SOURCE = """
model := "model.joblib"
target := score

[BOUND]:
forall x0
with domain(x0.a: [0.0, 1.0])
=> target[x0] <= 1.0 using Z3(phase_selection=2)
"""


def test_backend_arguments_fail_explicitly_at_semantic_boundary() -> None:
    with pytest.raises(
        SemanticError,
        match="Backend arguments are parsed and preserved",
    ):
        run_ir(_SOURCE, model_schema=numeric_schema())
