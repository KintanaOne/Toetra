from __future__ import annotations

from dsl.backends.router import BackendRoute
from dsl.backends.z3_backend.capabilities import Z3_CAPABILITIES
from dsl.backends.z3_backend.runner import Z3Runner
from dsl.language.vocabulary.backends import EnumBackend
from dsl.reporting.builder import build_verification_report
from test.unit.backends.z3_backend._point_aware_helpers import build_task

_SOURCE = """
model := "linear.joblib"
target := score

[LOGIC]:
exists x0, x1
with domain(
    x0.a: [0.0, 3.0],
    x1.a: [0.0, 3.0]
)
where x1.a > x0.a
=> target[x1] > target[x0] using Z3
"""


def _report():
    task = build_task(_SOURCE)
    result = Z3Runner().run(task)
    route = BackendRoute(
        backend=EnumBackend.Z3,
        reason="test route",
        capabilities=Z3_CAPABILITIES,
    )
    return build_verification_report(task, route, result, property_index=0)


def test_res_pnt_002_two_points_are_grouped_without_flattening() -> None:
    report = _report()

    assert [point.name for point in report.points] == ["x0", "x1"]
    assert set(report.point_values) == {"x0", "x1"}
    assert set(report.output_values_by_point) == {"x0", "x1"}

    try:
        report.input_values
    except ValueError as error:
        assert "multiple points" in str(error)
    else:
        raise AssertionError("multi-point inputs must not be flattened")

    try:
        report.output_values
    except ValueError as error:
        assert "multiple points" in str(error)
    else:
        raise AssertionError("multi-point outputs must not be flattened")


def test_res_pnt_003_existential_result_keeps_witness_point_roles() -> None:
    report = _report()

    assert report.status.value == "witness"
    assert {point.binding_kind for point in report.points} == {"existential"}
    assert "Point x0" in report.to_text()
    assert "Point x1" in report.to_text()


def test_res_pnt_json_exposes_structured_point_evidence() -> None:
    payload = _report().to_dict()

    assert [point["name"] for point in payload["points"]] == ["x0", "x1"]
    assert payload["points"][0]["binding_kind"] == "existential"
    assert payload["points"][0]["outputs"][0]["target"] == "score"
