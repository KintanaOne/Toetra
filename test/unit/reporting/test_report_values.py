from __future__ import annotations

from fractions import Fraction

import z3

from dsl.reporting.model import ReportAssignment, ReportAssignmentKind


def test_assignment_exposes_exact_and_python_values() -> None:
    rational = ReportAssignment(
        raw_name="x0.ratio",
        display_name="x0.ratio",
        value=z3.RealVal("1/3"),
        kind=ReportAssignmentKind.INPUT,
    )
    integer = ReportAssignment(
        raw_name="x0.count",
        display_name="x0.count",
        value=z3.IntVal(3),
        kind=ReportAssignmentKind.INPUT,
    )

    assert rational.exact_value == Fraction(1, 3)
    assert rational.python_value == float(Fraction(1, 3))
    assert rational.field_name == "ratio"
    assert integer.exact_value == 3
    assert integer.python_value == 3
    assert integer.field_name == "count"
