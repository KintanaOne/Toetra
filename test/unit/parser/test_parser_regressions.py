from __future__ import annotations

import pytest

from dsl.parser.parser import parse_toetra_code


@pytest.mark.parametrize(
    "source",
    [
        pytest.param(
            """
            model := "demo.onnx"
            target := MyTarget

            [LOGIC]:
            check_at x0
                => target <= 7
                using Z3
            """,
            id="pointwise-check-at",
        ),
        pytest.param(
            """
            model := "demo.onnx"
            target := MyTarget

            [LOGIC]:
            at x0
                => x0.a <= 7
                using Z3
            """,
            id="local-at",
        ),
        pytest.param(
            """
            model := "demo.onnx"
            target := MyTarget

            [ROBUSTNESS]:
            x ~ x' in neighborhood(L2, eps=0.01)
                => x.a <= 7
                using Z3
            """,
            id="pairwise-neighborhood",
        ),
    ],
)
def test_existing_non_quantified_scopes_still_parse(source: str) -> None:
    parse_toetra_code(source)
