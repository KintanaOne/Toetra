from __future__ import annotations

import pytest

from dsl.builder.program import parse_program
from dsl.parser.errors import ParserError
from dsl.parser.parser import parse_toetra_code
from dsl.semantic.core.specification_constants import SPECIFICATION_CONSTANT_KIND
from dsl.semantic.core.validator import ToetraValidator
from dsl.semantic.runtime.tracer import ValidationTracer


def _build_and_validate(source: str):
    program = parse_program(parse_toetra_code(source))
    ToetraValidator().validate(
        program,
        tracer=ValidationTracer(enabled=False),
    )
    return program


def test_unique_specification_constants_register_for_every_property() -> None:
    program = _build_and_validate("""
        model := "model.onnx"
        target := MyTarget

        threshold := 7

        [LOGIC]:
        forall x0 => x0.a <= threshold

        [LOGIC]:
        exists candidate => candidate.a >= threshold
        """)

    for prop in program.body:
        assert prop.semantic is not None
        assert prop.semantic.symbol_table is not None

        symbol = prop.semantic.symbol_table.resolve("threshold")

        assert symbol is not None
        assert symbol.kind == SPECIFICATION_CONSTANT_KIND
        assert symbol.origin is program.header.specification_constants[0]


def test_duplicate_specification_constant_is_rejected() -> None:
    program = parse_program(parse_toetra_code("""
        model := "model.onnx"
        target := MyTarget

        threshold := 7
        threshold := 8

        [LOGIC]:
        forall x0 => target <= 1
        """))

    with pytest.raises(
        ParserError,
        match="Duplicate specification constant 'threshold'",
    ):
        ToetraValidator().validate(program, tracer=ValidationTracer(enabled=False))


def test_scope_variable_collision_is_rejected() -> None:
    program = parse_program(parse_toetra_code("""
        model := "model.onnx"
        target := MyTarget

        applicant := 7

        [LOGIC]:
        forall applicant => target <= 1
        """))

    with pytest.raises(ParserError, match="collides with a scope variable"):
        ToetraValidator().validate(program, tracer=ValidationTracer(enabled=False))
