from __future__ import annotations

import pytest

from toetra._compiler.builder.program import parse_program
from toetra._compiler.parser.parser import parse_toetra_code
from toetra._compiler.semantic.core.property import PropertyValidator
from toetra._compiler.semantic.core.validator import ToetraValidator
from toetra._compiler.semantic.errors.errors import SemanticError
from toetra._compiler.semantic.runtime.tracer import ValidationTracer


def test_semantic_validator_preserves_semantic_error_family_and_location() -> None:
    source = """
model := "model.joblib"
target := score

[LOGIC]:
forall x0 => y.a <= 7.0
"""
    program = parse_program(parse_toetra_code(source))

    with pytest.raises(SemanticError) as caught:
        ToetraValidator().validate(
            program,
            tracer=ValidationTracer(enabled=False),
        )

    error = caught.value
    assert error.code.startswith("SEMANTIC_")
    assert error.line is not None
    assert error.column is not None


def test_semantic_validator_does_not_relabel_internal_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    program = parse_program(parse_toetra_code("""
model := "model.joblib"
target := score

[LOGIC]:
forall x0 => x0.a <= 7.0
"""))

    def fail_validation(
        self: PropertyValidator,
        *args: object,
        **kwargs: object,
    ) -> bool:
        raise RuntimeError("internal semantic implementation failure")

    monkeypatch.setattr(PropertyValidator, "validate", fail_validation)

    with pytest.raises(RuntimeError, match="internal semantic implementation failure"):
        ToetraValidator().validate(
            program,
            tracer=ValidationTracer(enabled=False),
        )
