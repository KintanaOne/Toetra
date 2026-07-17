from __future__ import annotations

import pytest

from dsl.parser.errors import ParserError
from dsl.semantic.core.validator import FORMLValidator
from dsl.semantic.runtime.tracer import ValidationTracer
from test.unit.semantic.anchor_helpers import (
    anchor_schema,
    build_program,
    validate_program,
)


def _assert_schema_rejected(source: str, message: str) -> None:
    program = build_program(source)
    with pytest.raises(ParserError, match=message):
        FORMLValidator().validate(
            program,
            tracer=ValidationTracer(enabled=False),
            model_schema=anchor_schema(),
        )


def test_sem_anchor_005_rejects_unknown_model_feature() -> None:
    _assert_schema_rejected(
        """
        model := "model.onnx"
        target := score

        anchor baseline := {
            age: 42,
            income: 55000,
            active: true,
            raw_customer_id: "C-1842"
        }

        [BOUND]:
        check_at baseline => target <= 1
        """,
        "Unknown model feature 'raw_customer_id'",
    )


def test_sem_anchor_006_rejects_incomplete_inline_anchor() -> None:
    _assert_schema_rejected(
        """
        model := "model.onnx"
        target := score

        anchor baseline := {
            age: 42,
            income: 55000
        }

        [BOUND]:
        check_at baseline => target <= 1
        """,
        "Incomplete anchor 'baseline'.*active",
    )


def test_sem_anchor_007_rejects_incompatible_literal_dtype() -> None:
    _assert_schema_rejected(
        """
        model := "model.onnx"
        target := score

        anchor baseline := {
            age: "forty-two",
            income: 55000,
            active: true
        }

        [BOUND]:
        check_at baseline => target <= 1
        """,
        "feature 'age' expects int, got string",
    )


def test_integer_literal_is_safely_widened_for_float_feature() -> None:
    program = validate_program("""
        model := "model.onnx"
        target := score

        anchor baseline := {
            age: 42,
            income: 55000,
            active: true
        }

        [BOUND]:
        check_at baseline => target <= 1
        """)

    annotation = program.body[0].semantic
    assert annotation is not None
    assert annotation.context is not None
