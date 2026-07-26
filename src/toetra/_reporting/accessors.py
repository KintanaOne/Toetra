"""Compatibility-safe accessors for grouped reporting evidence.

The reporting model evolved during the point-binding migration. Runtime consumers
must depend on the stable semantic shape (point inputs and outputs), not on one
specific dataclass layout. These helpers support both the canonical schema-v2
objects and the earlier evidence objects kept in the full repository during the
migration window.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from toetra._reporting.values import python_report_value


def point_input_values(point: object) -> dict[str, Any]:
    """Return one point's input values without assuming its concrete class."""

    direct = _mapping_attribute(point, "input_values")
    if direct is not None:
        return direct
    return _assignment_values(
        point,
        collection_names=("inputs", "features", "input_evidence"),
        name_candidates=("field_name", "feature_name", "name"),
    )


def point_output_values(point: object) -> dict[str, Any]:
    """Return one point's model outputs without assuming its concrete class."""

    direct = _mapping_attribute(point, "output_values")
    if direct is not None:
        return direct
    return _assignment_values(
        point,
        collection_names=("outputs", "output_evidence"),
        name_candidates=("field_name", "target_name", "name"),
    )


def report_point_values(report: object) -> dict[str, dict[str, Any]]:
    """Return inputs grouped by semantic point identity."""

    direct = _nested_mapping_attribute(report, "point_values")
    if direct is not None:
        return direct
    return _values_by_point(report, point_input_values)


def report_output_values_by_point(report: object) -> dict[str, dict[str, Any]]:
    """Return outputs grouped by semantic point identity."""

    direct = _nested_mapping_attribute(report, "output_values_by_point")
    if direct is not None:
        return direct
    return _values_by_point(report, point_output_values)


def _values_by_point(
    report: object,
    accessor: Any,
) -> dict[str, dict[str, Any]]:
    points = getattr(report, "points", ())
    if not isinstance(points, Iterable) or isinstance(points, (str, bytes, Mapping)):
        return {}

    grouped: dict[str, dict[str, Any]] = {}
    for point in points:
        name = getattr(point, "name", None)
        if not isinstance(name, str) or not name:
            continue
        values = accessor(point)
        if values:
            grouped[name] = values
    return grouped


def _assignment_values(
    owner: object,
    *,
    collection_names: tuple[str, ...],
    name_candidates: tuple[str, ...],
) -> dict[str, Any]:
    assignments: object | None = None
    for collection_name in collection_names:
        candidate = getattr(owner, collection_name, None)
        if candidate is not None:
            assignments = candidate
            break

    if isinstance(assignments, Mapping):
        return {
            str(name): python_report_value(value) for name, value in assignments.items()
        }
    if not isinstance(assignments, Iterable) or isinstance(assignments, (str, bytes)):
        return {}

    values: dict[str, Any] = {}
    for assignment in assignments:
        name = _assignment_name(assignment, name_candidates)
        if name is None:
            continue
        raw_value = _assignment_value(assignment)
        values[name] = python_report_value(raw_value)
    return values


def _assignment_name(
    assignment: object,
    candidates: tuple[str, ...],
) -> str | None:
    for candidate in candidates:
        value = getattr(assignment, candidate, None)
        if isinstance(value, str) and value:
            return value

    assignment_name = getattr(assignment, "assignment_name", None)
    if not isinstance(assignment_name, str) or not assignment_name:
        assignment_name = getattr(assignment, "display_name", None)
    if not isinstance(assignment_name, str) or not assignment_name:
        return None

    without_index = assignment_name.split("[", 1)[0]
    return without_index.rsplit(".", 1)[-1]


def _assignment_value(assignment: object) -> Any:
    for candidate in ("python_value", "formal_value", "value"):
        sentinel = object()
        value = getattr(assignment, candidate, sentinel)
        if value is not sentinel:
            return value
    return None


def _mapping_attribute(owner: object, name: str) -> dict[str, Any] | None:
    value = getattr(owner, name, None)
    if not isinstance(value, Mapping):
        return None
    return {str(key): item for key, item in value.items()}


def _nested_mapping_attribute(
    owner: object,
    name: str,
) -> dict[str, dict[str, Any]] | None:
    value = getattr(owner, name, None)
    if not isinstance(value, Mapping):
        return None

    grouped: dict[str, dict[str, Any]] = {}
    for point_name, point_values in value.items():
        if not isinstance(point_values, Mapping):
            return None
        grouped[str(point_name)] = {
            str(field_name): field_value
            for field_name, field_value in point_values.items()
        }
    return grouped
