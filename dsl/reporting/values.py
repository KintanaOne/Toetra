from __future__ import annotations

from dataclasses import asdict, is_dataclass
from decimal import Decimal
from enum import Enum
from fractions import Fraction
from typing import Any, Callable, Mapping, cast


def exact_report_value(value: Any) -> Any:
    """Return a backend-neutral exact value when one can be recovered safely."""

    if value is None or isinstance(value, (bool, int, float, str, Decimal, Fraction)):
        return value

    if isinstance(value, Enum):
        return exact_report_value(value.value)

    numerator = getattr(value, "numerator_as_long", None)
    denominator = getattr(value, "denominator_as_long", None)
    if callable(numerator) and callable(denominator):
        numerator_fn = cast(Callable[[], int], numerator)
        denominator_fn = cast(Callable[[], int], denominator)
        return Fraction(numerator_fn(), denominator_fn())

    as_long = getattr(value, "as_long", None)
    if callable(as_long):
        as_long_fn = cast(Callable[[], int], as_long)
        try:
            return as_long_fn()
        except (ArithmeticError, TypeError, ValueError):
            pass

    item = getattr(value, "item", None)
    if callable(item):
        try:
            return exact_report_value(item())
        except (TypeError, ValueError):
            pass

    return value


def python_report_value(value: Any) -> Any:
    """Convert a backend value to a convenient Python value for application code."""

    exact = exact_report_value(value)
    if isinstance(exact, Fraction):
        if exact.denominator == 1:
            return exact.numerator
        return float(exact)
    if isinstance(exact, Decimal):
        return float(exact)
    if exact is None or isinstance(exact, (bool, int, float, str)):
        return exact
    return str(exact)


def json_safe_report_value(value: Any) -> Any:
    """Convert a backend value to the stable Toetra JSON representation."""

    exact = exact_report_value(value)
    if exact is None or isinstance(exact, (bool, int, float, str)):
        return exact

    if isinstance(exact, Decimal):
        return str(exact)

    if isinstance(exact, Fraction):
        if exact.denominator == 1:
            return exact.numerator
        return {
            "kind": "rational",
            "numerator": exact.numerator,
            "denominator": exact.denominator,
            "text": f"{exact.numerator}/{exact.denominator}",
        }

    if isinstance(exact, Mapping):
        return {str(key): json_safe_report_value(item) for key, item in exact.items()}

    if isinstance(exact, (list, tuple, set, frozenset)):
        return [json_safe_report_value(item) for item in exact]

    if is_dataclass(exact) and not isinstance(exact, type):
        return json_safe_report_value(asdict(exact))

    return str(exact)
