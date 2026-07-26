from __future__ import annotations

import pytest

from toetra._backends.defaults import create_default_backend_registry
from toetra._backends.errors import (
    NoCompatibleBackendError,
    UnsupportedBackendRequirementsError,
)
from toetra._backends.results import VerificationStatus
from toetra._backends.router import BackendRouter
from toetra._backends.z3_backend.translator import Z3Translator
from toetra._compiler.ir.ir2.run_ir2 import run_ir2_with_model_schema
from toetra._runtime import verify
from toetra._models.runtime.manager import ModelManager
from test.e2e.point_binding._helpers import build_linear_artifacts, source


def test_e2e_03_two_point_universal_property_proves_positive_slope(tmp_path) -> None:
    artifacts = build_linear_artifacts(
        tmp_path,
        feature_names=("a",),
        coefficients=(2.0,),
        intercept=1.0,
    )

    session = verify(
        source("e2e_03_two_point_universal"),
        model=artifacts.model_path,
        dataset=artifacts.dataset_path,
    )

    assert session.reports[0].status is VerificationStatus.PROVED
    task = session.executions[0].task
    assert [mapping.source_name for mapping in task.point_mappings] == ["x0", "x1"]
    assert {evaluation.point.name for evaluation in task.model_evaluations} == {
        "x0",
        "x1",
    }


def test_e2e_03_two_point_counterexample_is_grouped_and_replayable(tmp_path) -> None:
    artifacts = build_linear_artifacts(
        tmp_path,
        feature_names=("a",),
        coefficients=(-2.0,),
        intercept=1.0,
    )

    session = verify(
        source("e2e_03_two_point_universal"),
        model=artifacts.model_path,
        dataset=artifacts.dataset_path,
    )

    finding = session.first_counterexample
    assert finding is not None
    assert finding.status is VerificationStatus.COUNTEREXAMPLE
    assert tuple(finding.point_values) == ("x0", "x1")
    assert tuple(finding.output_values_by_point) == ("x0", "x1")
    with pytest.raises(ValueError, match="multiple points"):
        _ = finding.input_values

    replay = finding.replay()
    assert replay.is_consistent is True, replay.to_text()
    assert replay.relation_consistent is True
    assert replay.assertion_consistent is True
    assert replay.relation_satisfied is not False
    assert replay.assertion_satisfied is not True
    assert tuple(replay.inputs_by_point) == ("x0", "x1")
    assert tuple(replay.model_outputs_by_point) == ("x0", "x1")


def test_e2e_05_existential_adversarial_case_is_a_witness(tmp_path) -> None:
    artifacts = build_linear_artifacts(
        tmp_path,
        feature_names=("a",),
        coefficients=(3.0,),
        intercept=0.0,
    )

    session = verify(
        source("e2e_05_existential_witness"),
        model=artifacts.model_path,
        dataset=artifacts.dataset_path,
    )

    finding = session.first_witness
    assert finding is not None
    assert finding.status is VerificationStatus.WITNESS
    assert "Witness" in finding.report.summary
    assert "counterexample" not in finding.report.summary.lower()
    assert tuple(finding.point_values) == ("x0", "x1")
    assert tuple(finding.output_values_by_point) == ("x0", "x1")

    replay = finding.replay(tolerance=1e-8)
    assert replay.is_consistent is True, replay.to_text()
    assert replay.relation_consistent is True
    assert replay.assertion_consistent is True
    assert replay.relation_satisfied is not False
    assert replay.assertion_satisfied is not False


def test_e2e_06_alternating_quantifiers_are_rejected_before_translation(
    tmp_path,
) -> None:
    artifacts = build_linear_artifacts(
        tmp_path,
        feature_names=("a",),
        coefficients=(2.0,),
        intercept=1.0,
    )
    schema = ModelManager(
        model_path=artifacts.model_path,
        dataset_path=artifacts.dataset_path,
        target_name="score",
    ).build_schema()
    task = run_ir2_with_model_schema(
        source("e2e_06_alternating_quantifiers"),
        schema=schema,
    )[0]

    assert task.quantifier_structure.binder_sequence == ("forall", "exists")
    assert task.requirements.requires_quantifier_alternation is True
    assert task.requirements.requires_native_quantifiers is True

    route_message = (
        "Requested backend 'Z3' does not satisfy IR2 requirements: "
        "native quantifiers; quantifier alternation"
    )
    with pytest.raises(NoCompatibleBackendError, match=route_message):
        BackendRouter(create_default_backend_registry()).route(task)

    translator_message = (
        "Z3 does not satisfy IR2 requirements: native quantifiers; "
        "quantifier alternation"
    )
    with pytest.raises(UnsupportedBackendRequirementsError, match=translator_message):
        Z3Translator().translate(task)
