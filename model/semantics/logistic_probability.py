from __future__ import annotations

from dataclasses import dataclass
from decimal import (
    ROUND_CEILING,
    ROUND_FLOOR,
    Decimal,
    InvalidOperation,
    localcontext,
)

from dsl.language.vocabulary.operators import EnumComparisonOperator

LOGIT_BOUND_PRECISION_DIGITS = 50
LOGIT_BOUND_GUARD_DIGITS = 20
_MIN_LOGIT_BOUND_PRECISION_DIGITS = 16
_MIN_LOGIT_BOUND_GUARD_DIGITS = 8


@dataclass(frozen=True)
class LogitThresholdInterval:
    """Conservative decimal interval enclosing one logistic logit threshold."""

    probability: Decimal
    lower: Decimal
    upper: Decimal
    precision_digits: int
    working_precision_digits: int
    guard_digits: int
    exact: bool = False

    @property
    def expression(self) -> str:
        return f"logit({format(self.probability, 'f')})"

    def negated(self) -> LogitThresholdInterval:
        return LogitThresholdInterval(
            probability=self.probability,
            lower=-self.upper,
            upper=-self.lower,
            precision_digits=self.precision_digits,
            working_precision_digits=self.working_precision_digits,
            guard_digits=self.guard_digits,
            exact=self.exact,
        )

    def selected_bound(
        self,
        *,
        operator: EnumComparisonOperator,
        predicate_relation: str,
    ) -> tuple[Decimal, str]:
        """Select a bound preserving the requested predicate-set relation.

        ``predicate_relation='under'`` produces a canonical predicate whose
        satisfying set is contained in the source predicate. ``'over'``
        produces the converse inclusion. The latter is used under negative
        logical polarity so that the complete lowered formula remains an
        under-approximation of the user-visible formula.
        """

        if self.exact:
            return self.lower, "exact"
        if predicate_relation not in {"under", "over"}:
            raise ValueError("predicate_relation must be either 'under' or 'over'")

        greater = operator in {
            EnumComparisonOperator.GT,
            EnumComparisonOperator.GTE,
        }
        lower = operator in {
            EnumComparisonOperator.LT,
            EnumComparisonOperator.LTE,
        }
        if not greater and not lower:
            raise ValueError(
                "Logistic probability lowering supports only order comparisons"
            )

        if predicate_relation == "under":
            return (self.upper, "upper") if greater else (self.lower, "lower")
        return (self.lower, "lower") if greater else (self.upper, "upper")


def parse_probability_literal(*, value: object, source_lexeme: str | None) -> Decimal:
    """Parse a DSL probability threshold from its canonical source spelling."""

    raw = source_lexeme if source_lexeme is not None else str(value)
    try:
        probability = Decimal(raw)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Invalid probability threshold {raw!r}") from exc

    if not probability.is_finite():
        raise ValueError("Probability thresholds must be finite")
    if probability <= 0 or probability >= 1:
        raise ValueError(
            "The initial probability profile requires a threshold strictly "
            "between 0 and 1"
        )
    return probability


def _working_precision(
    probability: Decimal,
    *,
    precision_digits: int,
    guard_digits: int,
) -> int:
    """Return enough precision for guards and the complete source literal."""

    source_digits = len(probability.as_tuple().digits)
    return max(
        precision_digits + guard_digits,
        source_digits + guard_digits,
    )


def _rounded_log_interval(
    value: Decimal,
    *,
    working_precision_digits: int,
) -> tuple[Decimal, Decimal]:
    """Enclose ``ln(value)`` using neighbors of its correctly rounded value."""

    with localcontext() as context:
        context.prec = working_precision_digits
        rounded = value.ln(context=context)
        return rounded.next_minus(context), rounded.next_plus(context)


def _subtract_intervals(
    *,
    left_lower: Decimal,
    left_upper: Decimal,
    right_lower: Decimal,
    right_upper: Decimal,
    working_precision_digits: int,
) -> tuple[Decimal, Decimal]:
    """Subtract two intervals with directed rounding at working precision."""

    with localcontext() as lower_context:
        lower_context.prec = working_precision_digits
        lower_context.rounding = ROUND_FLOOR
        lower = lower_context.subtract(left_lower, right_upper)

    with localcontext() as upper_context:
        upper_context.prec = working_precision_digits
        upper_context.rounding = ROUND_CEILING
        upper = upper_context.subtract(left_upper, right_lower)

    return lower, upper


def _publish_interval(
    *,
    lower: Decimal,
    upper: Decimal,
    precision_digits: int,
) -> tuple[Decimal, Decimal]:
    """Round an internal enclosure outward to the declared public precision."""

    with localcontext() as lower_context:
        lower_context.prec = precision_digits
        lower_context.rounding = ROUND_FLOOR
        published_lower = +lower

    with localcontext() as upper_context:
        upper_context.prec = precision_digits
        upper_context.rounding = ROUND_CEILING
        published_upper = +upper

    return published_lower, published_upper


def logit_threshold_interval(
    probability: Decimal,
    *,
    precision_digits: int = LOGIT_BOUND_PRECISION_DIGITS,
    guard_digits: int = LOGIT_BOUND_GUARD_DIGITS,
) -> LogitThresholdInterval:
    """Return an outward decimal enclosure of ``logit(probability)``.

    The implementation evaluates the mathematically equivalent expression
    ``ln(p) - ln(1 - p)`` with interval arithmetic. Each logarithm is enclosed
    independently around its correctly rounded :class:`~decimal.Decimal`
    result. Interval subtraction uses directed rounding, then the final bounds
    are rounded outward to the declared precision.

    ``precision_digits`` controls the serialized bounds. ``guard_digits``
    controls internal working precision and does not replace the outward-rounding
    proof obligation. The native threshold ``p = 0.5`` is represented exactly
    as zero.
    """

    if precision_digits < _MIN_LOGIT_BOUND_PRECISION_DIGITS:
        raise ValueError(
            "Logit bounds require at least "
            f"{_MIN_LOGIT_BOUND_PRECISION_DIGITS} decimal digits"
        )
    if guard_digits < _MIN_LOGIT_BOUND_GUARD_DIGITS:
        raise ValueError(
            "Logit bounds require at least "
            f"{_MIN_LOGIT_BOUND_GUARD_DIGITS} guard digits"
        )
    if probability <= 0 or probability >= 1:
        raise ValueError("Logit is finite only for probabilities in (0, 1)")

    working_precision_digits = _working_precision(
        probability,
        precision_digits=precision_digits,
        guard_digits=guard_digits,
    )

    if probability == Decimal("0.5"):
        zero = Decimal(0)
        return LogitThresholdInterval(
            probability=probability,
            lower=zero,
            upper=zero,
            precision_digits=precision_digits,
            working_precision_digits=working_precision_digits,
            guard_digits=guard_digits,
            exact=True,
        )

    with localcontext() as subtraction_context:
        subtraction_context.prec = working_precision_digits
        complement = Decimal(1) - probability

    log_probability_lower, log_probability_upper = _rounded_log_interval(
        probability,
        working_precision_digits=working_precision_digits,
    )
    log_complement_lower, log_complement_upper = _rounded_log_interval(
        complement,
        working_precision_digits=working_precision_digits,
    )
    internal_lower, internal_upper = _subtract_intervals(
        left_lower=log_probability_lower,
        left_upper=log_probability_upper,
        right_lower=log_complement_lower,
        right_upper=log_complement_upper,
        working_precision_digits=working_precision_digits,
    )
    lower, upper = _publish_interval(
        lower=internal_lower,
        upper=internal_upper,
        precision_digits=precision_digits,
    )

    if lower > upper:
        raise ArithmeticError("Constructed logit interval is inverted")

    return LogitThresholdInterval(
        probability=probability,
        lower=lower,
        upper=upper,
        precision_digits=precision_digits,
        working_precision_digits=working_precision_digits,
        guard_digits=guard_digits,
        exact=False,
    )
