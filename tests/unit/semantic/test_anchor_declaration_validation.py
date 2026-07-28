from __future__ import annotations

import pytest

from toetra._compiler.semantic.errors.errors import SemanticError
from toetra._compiler.semantic.core.validator import ToetraValidator
from toetra._compiler.semantic.runtime.tracer import ValidationTracer
from tests.support.semantic_anchors import build_program


def _assert_rejected(source: str, message: str) -> None:
    program = build_program(source)
    with pytest.raises(SemanticError, match=message):
        ToetraValidator().validate(
            program,
            tracer=ValidationTracer(enabled=False),
        )


def test_sem_anchor_003_rejects_duplicate_anchor_identifier() -> None:
    _assert_rejected(
        """
        model := "model.onnx"
        target := score

        anchor baseline := { age: 42 }
        anchor baseline := { age: 43 }

        [BOUND]:
        check_at baseline => target <= 1
        """,
        "Duplicate anchor identifier 'baseline'",
    )


def test_sem_anchor_004_rejects_duplicate_inline_feature() -> None:
    _assert_rejected(
        """
        model := "model.onnx"
        target := score

        anchor baseline := {
            age: 42,
            age: 43
        }

        [BOUND]:
        check_at baseline => target <= 1
        """,
        "Duplicate feature 'age' in anchor 'baseline'",
    )
