from __future__ import annotations

import pytest

from toetra._compiler.parser.errors import ParserError
from toetra._compiler.semantic.core.validator import ToetraValidator
from toetra._compiler.semantic.runtime.tracer import ValidationTracer
from test.unit.semantic.anchor_helpers import build_program


def _assert_rejected(source: str, message: str) -> None:
    program = build_program(source)
    with pytest.raises(ParserError, match=message):
        ToetraValidator().validate(
            program,
            tracer=ValidationTracer(enabled=False),
        )


def test_referenced_anchor_rejects_duplicate_named_argument() -> None:
    _assert_rejected(
        """
        model := "model.onnx"
        target := score

        anchor customer := ref(
            key = "customer_id",
            key = "other_id",
            value = "C-1842"
        )

        [BOUND]:
        check_at customer => target <= 1
        """,
        "Duplicate ref argument 'key'",
    )


def test_referenced_anchor_rejects_missing_value_argument() -> None:
    _assert_rejected(
        """
        model := "model.onnx"
        target := score

        anchor customer := ref(key = "customer_id")

        [BOUND]:
        check_at customer => target <= 1
        """,
        "missing argument.*value",
    )


def test_referenced_anchor_requires_string_lookup_key() -> None:
    _assert_rejected(
        """
        model := "model.onnx"
        target := score

        anchor customer := ref(key = 123, value = "C-1842")

        [BOUND]:
        check_at customer => target <= 1
        """,
        "ref key must be a string literal",
    )
