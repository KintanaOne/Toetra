from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from toetra._reporting.accessors import (
    point_input_values,
    point_output_values,
    report_output_values_by_point,
)
from toetra._reporting.model import (
    ReportAssignment,
    ReportAssignmentKind,
    ReportPointEvidence,
)


@dataclass(frozen=True)
class LegacyInputEvidence:
    feature_name: str
    formal_value: Any
    assignment_name: str


@dataclass(frozen=True)
class LegacyOutputEvidence:
    model_identity: str
    target_name: str
    formal_value: Any
    assignment_name: str


@dataclass(frozen=True)
class LegacyPointEvidence:
    name: str
    input_values: dict[str, Any]
    outputs: tuple[LegacyOutputEvidence, ...]


@dataclass(frozen=True)
class LegacySequencePointEvidence:
    name: str
    features: tuple[LegacyInputEvidence, ...]
    outputs: tuple[LegacyOutputEvidence, ...]


@dataclass(frozen=True)
class LegacyReport:
    points: tuple[object, ...]


def test_accessors_read_canonical_grouped_evidence() -> None:
    point = ReportPointEvidence(
        name="x0",
        binding_kind="universal",
        inputs=(
            ReportAssignment(
                raw_name="x0.a",
                display_name="x0.a",
                value=1,
                kind=ReportAssignmentKind.INPUT,
                point_name="x0",
            ),
        ),
        outputs=(
            ReportAssignment(
                raw_name="_model.score[x0]",
                display_name="score[x0]",
                value=3,
                kind=ReportAssignmentKind.OUTPUT,
                point_name="x0",
                target_name="score",
            ),
        ),
    )

    assert point_input_values(point) == {"a": 1}
    assert point_output_values(point) == {"score": 3}


def test_accessors_read_legacy_mapping_and_output_evidence() -> None:
    point = LegacyPointEvidence(
        name="x0",
        input_values={"a": 1},
        outputs=(
            LegacyOutputEvidence(
                model_identity="model.joblib",
                target_name="score",
                formal_value=3,
                assignment_name="_model.score",
            ),
        ),
    )

    assert point_input_values(point) == {"a": 1}
    assert point_output_values(point) == {"score": 3}
    assert report_output_values_by_point(LegacyReport((point,))) == {"x0": {"score": 3}}


def test_accessors_read_legacy_input_evidence_sequence() -> None:
    point = LegacySequencePointEvidence(
        name="x1",
        features=(
            LegacyInputEvidence(
                feature_name="a",
                formal_value=2,
                assignment_name="x1.a",
            ),
        ),
        outputs=(),
    )

    assert point_input_values(point) == {"a": 2}
