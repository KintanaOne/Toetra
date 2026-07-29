from __future__ import annotations

from decimal import Decimal

from toetra._backends.defaults import create_default_backend_registry
from toetra._backends.router import BackendRouter
from toetra._backends.results import VerificationStatus
from toetra._backends.z3_backend.runner import Z3Runner
from toetra._compiler.ir.ir2.run_ir2 import run_ir2_with_model_schema
from toetra._reporting.builder import build_verification_report
from toetra._reporting.json import REPORT_SCHEMA_VERSION
from tests.support.binary_classification import (
    binary_label_property,
    binary_probability_property,
    make_sklearn_logistic_schema,
)
from tests.support.paths import GOLDEN_ROOT


def _report(source: str, *, intercept: float):
    schema = make_sklearn_logistic_schema(intercept=intercept)
    task = run_ir2_with_model_schema(source, schema=schema)[0]
    route = BackendRouter(create_default_backend_registry()).route(task)
    result = Z3Runner().run(task)
    report = build_verification_report(
        task,
        route,
        result,
        property_index=0,
        schema=schema,
    )
    return task, report


def test_label_report_preserves_public_intent_and_boundary_views() -> None:
    task, report = _report(
        binary_label_property(label="approved"),
        intercept=0.0,
    )

    assert report.status is VerificationStatus.COUNTEREXAMPLE
    assert report.specification == "_model.decision.label == 'approved'"
    assert "oriented_decision_value" not in report.specification
    assert task.source_spec_formula is not None

    evaluation = report.model_evaluations[0]
    assert evaluation.native_probability_threshold == "0.5"
    assert evaluation.native_decision_threshold == "0"
    assert evaluation.equality_label == "rejected"
    assert evaluation.predicted_label == "rejected"
    assert evaluation.probability_values == {
        "rejected": 0.5,
        "approved": 0.5,
    }
    assert all(
        item.source == "reconstructed_from_oriented_decision_value"
        and item.precision_digits == 50
        for item in evaluation.probabilities
    )
    assert evaluation.quantity_values == {"oriented_decision_value": 0}

    lowering = evaluation.lowerings[0]
    assert lowering.observable == "predicted_label"
    assert lowering.label == "approved"
    assert lowering.property_threshold is None
    assert lowering.property_value == "rejected"
    assert lowering.property_satisfied is False
    assert lowering.quantity_kind == "oriented_decision_value"
    assert lowering.quantity_value == 0
    assert lowering.canonical_margin == Decimal("0")


def test_probability_report_distinguishes_native_and_property_thresholds() -> None:
    _task, report = _report(
        binary_probability_property(
            quantifier="exists",
            threshold="0.8",
        ),
        intercept=2.0,
    )

    assert report.status is VerificationStatus.WITNESS
    evaluation = report.model_evaluations[0]
    lowering = evaluation.lowerings[0]

    assert evaluation.native_probability_threshold == "0.5"
    assert lowering.property_threshold == "0.8"
    assert lowering.property_value is not None
    assert lowering.property_value > Decimal("0.8")
    assert lowering.property_satisfied is True
    assert lowering.property_margin is not None
    assert lowering.property_margin > 0
    assert lowering.exact_threshold_expression == "logit(0.8)"
    assert lowering.threshold_lower_bound is not None
    assert lowering.threshold_upper_bound is not None
    assert lowering.selected_bound == "upper"
    assert lowering.transformation_version == "2"
    assert lowering.compatibility_classification == "sound_under_approximation"


def test_json_v6_preserves_classification_evaluations_without_reinterpreting_assignments() -> (
    None
):
    _task, report = _report(
        binary_label_property(label="approved"),
        intercept=0.0,
    )

    payload = report.to_dict()
    assert REPORT_SCHEMA_VERSION == 6
    assert payload["schema_version"] == 6
    assert payload["assignments"]["outputs"] == []
    assert payload["assignments"]["auxiliary"][0]["quantity_kind"] == (
        "oriented_decision_value"
    )
    evaluation = payload["model_evaluations"][0]
    assert evaluation["predicted_label"] == "rejected"
    assert evaluation["probabilities"][0]["source"] == (
        "reconstructed_from_oriented_decision_value"
    )
    assert evaluation["probabilities"][0]["precision_digits"] == 50
    assert evaluation["decision_policy"]["native_probability_threshold"] == "0.5"
    assert evaluation["lowerings"][0]["source_intent"]["label"] == "approved"


def test_text_and_html_render_classification_evidence() -> None:
    _task, report = _report(
        binary_probability_property(
            quantifier="exists",
            threshold="0.8",
        ),
        intercept=2.0,
    )

    text = report.to_text()
    html = report.to_html()
    assert "Model evaluations" in text
    assert "native decision" in text
    assert "probability('approved')" in text
    assert "source=reconstructed_from_oriented_decision_value" in text
    assert "semantic=binary_logistic_affine_classification" in text
    assert "Permitted conclusions" in html
    assert "source=reconstructed_from_oriented_decision_value" in html
    assert "semantic=binary_logistic_affine_classification" in html
    assert "logit(0.8)" in text
    assert "Model evaluations" in html
    assert "Native probability threshold" in html
    assert "Threshold evidence" in html


def test_historical_report_fixtures_remain_readable_json() -> None:
    import json

    fixture_dir = GOLDEN_ROOT / "reporting"
    versions = []
    for path in sorted(fixture_dir.glob("verification_report_v*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        version = payload["schema_version"]
        expected_schema = (
            "forml.verification-report"
            if version <= 5
            else "toetra.verification-report"
        )
        assert payload["schema"] == expected_schema
        versions.append(version)

    assert versions == [1, 2, 3, 4, 5, 6]


def test_pairwise_report_preserves_two_points_and_related_evidence() -> None:
    schema = make_sklearn_logistic_schema(coefficient=1.0, intercept=0.0)
    source = """\
model := "credit.joblib"
target := decision

[LOGIC]:
forall left, right
with domain(left.income: [1.0, 2.0], right.income: [-2.0, -1.0])
=> target[left].label == target[right].label using Z3
"""
    task = run_ir2_with_model_schema(source, schema=schema)[0]
    route = BackendRouter(create_default_backend_registry()).route(task)
    result = Z3Runner().run(task)
    report = build_verification_report(
        task, route, result, property_index=0, schema=schema
    )

    assert report.status is VerificationStatus.COUNTEREXAMPLE
    assert report.specification == "target[left].label == target[right].label"
    assert tuple(item.point_name for item in report.model_evaluations) == (
        "left",
        "right",
    )
    left, right = report.model_evaluations
    assert left.predicted_label == "approved"
    assert right.predicted_label == "rejected"
    trace = left.lowerings[0]
    assert trace.related_point_name == "right"
    assert trace.related_property_value == "rejected"
    assert trace.property_satisfied is False
    assert trace.canonical_formula_kind == "same_binary_decision_region"
    payload = report.to_dict()["model_evaluations"][0]["lowerings"][0]
    assert payload["source_intent"]["related_point"] == "right"
    assert (
        payload["canonical_constraint"]["formula_kind"] == "same_binary_decision_region"
    )
    assert "predicted_label[left] == predicted_label[right]" in report.to_text()
    assert "Related 1" in report.to_html()
