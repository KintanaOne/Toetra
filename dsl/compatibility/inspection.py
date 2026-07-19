from __future__ import annotations

import math
import numbers
from collections.abc import Mapping, Sequence
from dataclasses import fields, is_dataclass
from decimal import Decimal
from fractions import Fraction
from typing import Any


def contains_non_finite_numeric_values(value: object) -> bool:
    """Return whether a nested pre-backend artifact contains NaN or infinity."""

    return _contains_non_finite(value, seen=set())


def _contains_non_finite(value: object, *, seen: set[int]) -> bool:
    if value is None or isinstance(value, (str, bytes, bool, Fraction, int)):
        return False
    if isinstance(value, Decimal):
        return not value.is_finite()
    if isinstance(value, numbers.Real):
        return not math.isfinite(float(value))

    value_id = id(value)
    if value_id in seen:
        return False
    if is_dataclass(value) and not isinstance(value, type):
        seen.add(value_id)
        return any(
            _contains_non_finite(getattr(value, item.name), seen=seen)
            for item in fields(value)
        )
    if isinstance(value, Mapping):
        seen.add(value_id)
        return any(_contains_non_finite(item, seen=seen) for item in value.values())
    if isinstance(value, Sequence):
        seen.add(value_id)
        return any(_contains_non_finite(item, seen=seen) for item in value)

    item = _numpy_scalar_value(value)
    if item is not value:
        return _contains_non_finite(item, seen=seen)
    return False


def _numpy_scalar_value(value: object) -> Any:
    item = getattr(value, "item", None)
    if not callable(item):
        return value
    try:
        return item()
    except (TypeError, ValueError):
        return value
