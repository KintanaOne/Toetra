from __future__ import annotations

import pytest

from toetra._backends.z3_backend.runner import VerificationStatus, Z3Runner
from toetra._backends.z3_backend.translator import Z3Translator
from toetra._compiler.ir.ir2.run_ir2 import run_ir2_with_model_schema
from toetra._compiler.parser.errors import ParserError
from tests.support.backend_tasks import (
    build_task,
    linear_schema,
)


def test_be_nbh_001_linf_lowering_reaches_complete_multi_point_query() -> None:
    task = build_task(
        """
        model := "linear.joblib"
        target := score

        anchor x0 := {
            a: 1.0
        }

        [ROBUSTNESS]:
        forall x1
        where x1 in neighborhood(
            of = x0,
            metric = Linf,
            eps = 0.1
        )
        => (
            target[x1] - target[x0] <= 0.2
            and target[x0] - target[x1] <= 0.2
        ) using Z3
        """,
        coefficient=1.0,
    )

    translation = Z3Translator().translate(task)
    result = Z3Runner().run(task)

    assert {"x0.a", "x1.a"}.issubset(translation.variables)
    assert {"_model.score[x0]", "_model.score[x1]"}.issubset(translation.variables)
    assert result.status is VerificationStatus.PROVED


def test_be_nbh_002_unsupported_metric_is_rejected_before_backend_execution() -> None:
    with pytest.raises(ParserError, match="supported metric: Linf"):
        run_ir2_with_model_schema(
            """
            model := "linear.joblib"
            target := score

            anchor x0 := {
                a: 1.0
            }

            [ROBUSTNESS]:
            forall x1
            where x1 in neighborhood(
                of = x0,
                metric = L2,
                eps = 0.1
            )
            => target[x1] >= target[x0] using Z3
            """,
            schema=linear_schema(),
        )
