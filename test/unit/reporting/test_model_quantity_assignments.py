from __future__ import annotations

from dsl.backends.defaults import create_default_backend_registry
from dsl.backends.router import BackendRouter
from dsl.backends.z3_backend.runner import Z3Runner
from dsl.ir.ir2.run_ir2 import run_ir2_with_model_schema
from dsl.reporting.builder import build_verification_report
from dsl.reporting.model import ReportAssignmentKind
from test.fixtures.binary_classification import (
    binary_label_property,
    make_sklearn_logistic_schema,
)


def test_latent_model_quantity_is_reported_as_auxiliary_not_output() -> None:
    task = run_ir2_with_model_schema(
        binary_label_property(label="approved"),
        schema=make_sklearn_logistic_schema(intercept=0.0),
    )[0]
    route = BackendRouter(create_default_backend_registry()).route(task)
    result = Z3Runner().run(task)
    report = build_verification_report(task, route, result, property_index=0)
    quantities = tuple(
        assignment
        for assignment in report.assignments
        if "oriented_decision_value" in assignment.raw_name
    )
    assert len(quantities) == 1
    assert quantities[0].kind is ReportAssignmentKind.AUXILIARY
    assert quantities[0].point_name == "applicant"
    assert report.points[0].outputs == ()
