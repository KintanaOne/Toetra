from __future__ import annotations

from collections.abc import Iterable

from toetra._compatibility.errors import InvalidCompatibilityDescriptorError


def canonical_identifier(value: str, *, field_name: str) -> str:
    """Normalize one extensible registry identity or reject an empty value."""

    normalized = value.strip().lower()
    if not normalized:
        raise InvalidCompatibilityDescriptorError(
            f"Numeric compatibility field {field_name!r} cannot be empty."
        )
    return normalized


def canonical_optional_identifier(
    value: str | None,
    *,
    field_name: str,
) -> str | None:
    if value is None:
        return None
    return canonical_identifier(value, field_name=field_name)


def canonical_version(value: str, *, field_name: str) -> str:
    """Trim a version/opset while preserving its case-sensitive spelling."""

    normalized = value.strip()
    if not normalized:
        raise InvalidCompatibilityDescriptorError(
            f"Numeric compatibility field {field_name!r} cannot be empty."
        )
    return normalized


def canonical_optional_version(
    value: str | None,
    *,
    field_name: str,
) -> str | None:
    if value is None:
        return None
    return canonical_version(value, field_name=field_name)


def canonical_tags(values: Iterable[str]) -> frozenset[str]:
    return frozenset(
        canonical_identifier(value, field_name="property tag") for value in values
    )
