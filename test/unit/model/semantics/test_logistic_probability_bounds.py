from __future__ import annotations

from decimal import Decimal, localcontext

import pytest

from toetra._language.vocabulary.operators import EnumComparisonOperator
from toetra._models.semantics.logistic_probability import (
    LOGIT_BOUND_GUARD_DIGITS,
    LOGIT_BOUND_PRECISION_DIGITS,
    logit_threshold_interval,
)


def _higher_precision_reference(probability: Decimal) -> Decimal:
    source_digits = len(probability.as_tuple().digits)
    with localcontext() as context:
        context.prec = max(160, source_digits + 100)
        return probability.ln(context=context) - (Decimal(1) - probability).ln(
            context=context
        )


@pytest.mark.parametrize(
    "probability",
    [
        Decimal("0.2"),
        Decimal("0.3"),
        Decimal("0.7"),
        Decimal("0.8"),
        Decimal("0.95"),
        Decimal("0.0000000000000000000000001"),
        Decimal("0.9999999999999999999999999"),
    ],
)
def test_logit_interval_contains_higher_precision_reference(
    probability: Decimal,
) -> None:
    interval = logit_threshold_interval(probability, precision_digits=40)
    reference = _higher_precision_reference(probability)

    assert interval.lower <= reference <= interval.upper
    assert interval.lower < interval.upper


def test_regression_ratio_rounding_cannot_escape_interval() -> None:
    """Regression for the pre-P21.8.1 rounded-ratio implementation.

    At 50 digits, computing ``ln(round(p / (1 - p)))`` first produced an upper
    bound below the exact logit for ``p = 0.7``. The independent logarithm
    intervals must contain the higher-precision reference.
    """

    probability = Decimal("0.7")
    interval = logit_threshold_interval(probability)
    reference = _higher_precision_reference(probability)

    assert interval.lower <= reference <= interval.upper


def test_declared_and_working_precision_are_recorded() -> None:
    interval = logit_threshold_interval(Decimal("0.8"))

    assert interval.precision_digits == LOGIT_BOUND_PRECISION_DIGITS
    assert interval.guard_digits == LOGIT_BOUND_GUARD_DIGITS
    assert interval.working_precision_digits == (
        LOGIT_BOUND_PRECISION_DIGITS + LOGIT_BOUND_GUARD_DIGITS
    )


def test_working_precision_preserves_long_source_literal() -> None:
    probability = Decimal(
        "0.123456789012345678901234567890123456789012345678901234567890"
    )
    interval = logit_threshold_interval(probability, precision_digits=40)

    assert interval.working_precision_digits >= (
        len(probability.as_tuple().digits) + interval.guard_digits
    )
    assert interval.lower <= _higher_precision_reference(probability) <= interval.upper


def test_selected_bounds_preserve_requested_predicate_relation() -> None:
    interval = logit_threshold_interval(Decimal("0.8"), precision_digits=40)

    threshold, side = interval.selected_bound(
        operator=EnumComparisonOperator.GTE,
        predicate_relation="under",
    )
    assert threshold == interval.upper
    assert side == "upper"

    threshold, side = interval.selected_bound(
        operator=EnumComparisonOperator.GTE,
        predicate_relation="over",
    )
    assert threshold == interval.lower
    assert side == "lower"


def test_negated_interval_preserves_precision_metadata() -> None:
    interval = logit_threshold_interval(Decimal("0.8"), precision_digits=40)
    negated = interval.negated()

    assert negated.lower == -interval.upper
    assert negated.upper == -interval.lower
    assert negated.precision_digits == interval.precision_digits
    assert negated.working_precision_digits == interval.working_precision_digits
    assert negated.guard_digits == interval.guard_digits


def test_half_probability_has_exact_zero_logit() -> None:
    interval = logit_threshold_interval(Decimal("0.5"))

    assert interval.exact is True
    assert interval.lower == interval.upper == Decimal(0)
    assert interval.precision_digits == LOGIT_BOUND_PRECISION_DIGITS
    assert interval.working_precision_digits == (
        LOGIT_BOUND_PRECISION_DIGITS + LOGIT_BOUND_GUARD_DIGITS
    )


@pytest.mark.parametrize(
    ("precision_digits", "guard_digits", "message"),
    [
        (15, LOGIT_BOUND_GUARD_DIGITS, "at least 16 decimal digits"),
        (LOGIT_BOUND_PRECISION_DIGITS, 7, "at least 8 guard digits"),
    ],
)
def test_logit_interval_rejects_unsafe_precision_policy(
    precision_digits: int,
    guard_digits: int,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        logit_threshold_interval(
            Decimal("0.8"),
            precision_digits=precision_digits,
            guard_digits=guard_digits,
        )
