from __future__ import annotations

import pytest

from toetra._compiler.ast.nodes.expressions import AtExprNode
from toetra._compiler.builder.errors import BuilderError
from toetra._compiler.builder.program import parse_program
from toetra._compiler.parser.parser import parse_toetra_code


def _program(body: str, *, property_type: str = "BOUND"):
    source = f"""
model := "model.joblib"
target := score

[{property_type}]:
{body}
"""
    return parse_program(parse_toetra_code(source))


def test_backend_arguments_are_typed_and_preserved_in_ast() -> None:
    program = _program(
        '1 <= 1 using Z3(phase_selection=2, trace=true, "label"="stable")'
    )
    backend = program.body[0].backend

    assert backend is not None
    assert tuple((item.key, item.value) for item in backend.args) == (
        ("phase_selection", 2),
        ("trace", True),
        ("label", "stable"),
    )


@pytest.mark.parametrize(
    "backend_call",
    (
        "Z3(1)",
        "Z3(trace)",
        "Z3(trace=true, trace=false)",
    ),
)
def test_invalid_backend_arguments_are_rejected_instead_of_dropped(
    backend_call: str,
) -> None:
    with pytest.raises(BuilderError):
        _program(f"1 <= 1 using {backend_call}")


def test_problem_function_arguments_are_rejected_instead_of_dropped() -> None:
    with pytest.raises(BuilderError, match="Problem-function arguments"):
        _program("CLASSIFICATION.EQUAL(1) using Z3", property_type="LOGIC")


def test_legacy_neighborhood_arguments_are_typed_and_preserved() -> None:
    program = _program(
        "at x0 in neighborhood(L2, eps=0.1, enabled=true) "
        "=> target[x0] <= 1 using Z3",
        property_type="ROBUSTNESS",
    )
    scope = program.body[0].rule.scope

    assert isinstance(scope, AtExprNode)
    assert scope.neighborhood is not None
    assert tuple((item.key, item.value) for item in scope.neighborhood.args) == (
        ("eps", 0.1),
        ("enabled", True),
    )


def test_duplicate_legacy_neighborhood_arguments_are_rejected() -> None:
    with pytest.raises(BuilderError, match="Duplicate neighborhood argument 'eps'"):
        _program(
            "at x0 in neighborhood(L2, eps=0.1, eps=0.2) "
            "=> target[x0] <= 1 using Z3",
            property_type="ROBUSTNESS",
        )
