from __future__ import annotations

import pytest

from toetra._compiler.ir.ir1.run_ir1 import run_ir
from toetra._models.semantics.errors import UnsupportedObservableLoweringError
from toetra._models.semantics.lowering import ModelSemanticLowerer
from test.fixtures.model_semantic_lowering import make_binary_logistic_schema


def test_probability_arithmetic_is_explicitly_deferred() -> None:
    schema = make_binary_logistic_schema()
    task = run_ir(
        """
        model := "credit.joblib"
        target := decision
        [LOGIC]:
        forall applicant =>
            target[applicant].probability("approved") + 0.1 >= 0.8
        """,
        model_schema=schema,
    )[0]

    with pytest.raises(
        UnsupportedObservableLoweringError,
        match="arithmetic over probabilities",
    ):
        ModelSemanticLowerer().lower_task(task, schema=schema)


def test_probability_to_probability_lowering_is_explicitly_deferred() -> None:
    schema = make_binary_logistic_schema()
    task = run_ir(
        """
        model := "credit.joblib"
        target := decision
        [LOGIC]:
        forall left, right =>
            target[left].probability("approved")
            >= target[right].probability("approved")
        """,
        model_schema=schema,
    )[0]
    with pytest.raises(
        UnsupportedObservableLoweringError, match="predicted-label relations only"
    ):
        ModelSemanticLowerer().lower_task(task, schema=schema)
