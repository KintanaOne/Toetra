from __future__ import annotations

import pytest

from dsl.ir.ir1.nodes import (
    LogicalIR,
    AndIR,
    ComparisonIR,
    ConstantExpressionIR,
    ImplyIR,
    NotIR,
    OrIR,
)
from dsl.language.vocabulary.operators import EnumComparisonOperator
from dsl.runtime.replay import (
    CounterexampleReplay,
    _evaluate_logical,
)
from dsl.semantic.types.enums import EnumDataType


def _constant(value: float) -> ConstantExpressionIR:
    return ConstantExpressionIR(value=value, dtype=EnumDataType.FLOAT)


def _comparison(
    left: float,
    operator: EnumComparisonOperator,
    right: float,
) -> ComparisonIR:
    return ComparisonIR(
        left=_constant(left),
        op=operator,
        right=_constant(right),
    )


def _evaluate(node: LogicalIR, *, tolerance: float = 1e-8) -> bool | None:
    return _evaluate_logical(node, {}, {}, tolerance=tolerance)


def test_numeric_ordering_inside_tolerance_band_is_indeterminate() -> None:
    assert _evaluate(_comparison(0.2 - 1e-15, EnumComparisonOperator.GT, 0.2)) is None
    assert _evaluate(_comparison(0.1 + 1e-16, EnumComparisonOperator.LTE, 0.1)) is None


def test_numeric_ordering_outside_tolerance_band_remains_decisive() -> None:
    assert _evaluate(_comparison(0.21, EnumComparisonOperator.GT, 0.2)) is True
    assert _evaluate(_comparison(0.19, EnumComparisonOperator.GT, 0.2)) is False


def test_zero_tolerance_preserves_exact_ordering_semantics() -> None:
    boundary = _comparison(0.2, EnumComparisonOperator.GT, 0.2)

    assert _evaluate(boundary, tolerance=0.0) is False


def test_numeric_equality_uses_absolute_replay_tolerance() -> None:
    assert _evaluate(_comparison(1.0, EnumComparisonOperator.EQ, 1.0 + 1e-10)) is True
    assert _evaluate(_comparison(1.0, EnumComparisonOperator.NEQ, 1.0 + 1e-10)) is False
    assert _evaluate(_comparison(1.0, EnumComparisonOperator.EQ, 1.1)) is False
    assert _evaluate(_comparison(1.0, EnumComparisonOperator.NEQ, 1.1)) is True


def test_three_valued_logic_preserves_decisive_operands() -> None:
    boundary = _comparison(0.2, EnumComparisonOperator.GT, 0.2)
    true_atom = _comparison(0.3, EnumComparisonOperator.GT, 0.2)
    false_atom = _comparison(0.1, EnumComparisonOperator.GT, 0.2)

    assert _evaluate(AndIR([boundary, true_atom])) is None
    assert _evaluate(AndIR([boundary, false_atom])) is False
    assert _evaluate(OrIR([boundary, false_atom])) is None
    assert _evaluate(OrIR([boundary, true_atom])) is True
    assert _evaluate(NotIR(boundary)) is None
    assert _evaluate(ImplyIR(boundary, false_atom)) is None


def test_indeterminate_boundary_does_not_contradict_formal_witness() -> None:
    replay = CounterexampleReplay(
        property_index=0,
        points={},
        relation_satisfied=None,
        assertion_satisfied=None,
        expected_assertion_satisfied=True,
        tolerance=1e-8,
    )

    assert replay.relation_consistent is True
    assert replay.assertion_consistent is True
    assert replay.is_consistent is True


def test_decisive_concrete_contradiction_remains_inconsistent() -> None:
    replay = CounterexampleReplay(
        property_index=0,
        points={},
        relation_satisfied=True,
        assertion_satisfied=False,
        expected_assertion_satisfied=True,
        tolerance=1e-8,
    )

    assert replay.assertion_consistent is False
    assert replay.is_consistent is False


def test_replay_rejects_invalid_tolerance() -> None:
    with pytest.raises(ValueError, match="finite non-negative"):
        CounterexampleReplay(
            property_index=0,
            points={},
            relation_satisfied=True,
            assertion_satisfied=True,
            expected_assertion_satisfied=True,
            tolerance=-1.0,
        )
