from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import pandas as pd
from sklearn.linear_model import LogisticRegression

from toetra._backends.defaults import create_default_backend_registry
from toetra._backends.router import BackendRouter
from toetra._backends.results import VerificationStatus
from toetra._backends.z3_backend.runner import Z3Runner
from toetra._compiler.ir.ir2.run_ir2 import run_ir2_with_model_schema
from toetra._reporting.builder import build_verification_report
from toetra._runtime.model_observer import (
    ModelObservation,
    ModelObserverRegistry,
)
from toetra._runtime.replay_engine import replay_verification_report
from toetra._runtime.session import VerificationFinding
from toetra._models.introspector.sklearn_introspector import SklearnIntrospector


def _artifacts(tmp_path):
    frame = pd.DataFrame(
        {
            "income": [-3.0, -2.0, -1.0, 1.0, 2.0, 3.0],
            "decision": [0, 0, 0, 1, 1, 1],
        }
    )
    model = LogisticRegression(random_state=0, max_iter=1000).fit(
        frame[["income"]], frame["decision"]
    )
    dataset = tmp_path / "classification.csv"
    frame.to_csv(dataset, index=False)
    schema = SklearnIntrospector(
        model=model,
        source_path=dataset,
        target_name="decision",
    ).introspect()
    return model, schema


def _compile_report(source: str, schema):
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


def test_counterexample_replay_compares_label_probability_quantity_and_property(
    tmp_path,
) -> None:
    model, schema = _artifacts(tmp_path)
    source = """
model := "binary.joblib"
target := decision

[LOGIC]:
forall applicant
with domain(applicant.income: [-3.0, -1.0])
=> target[applicant].label == 1 using Z3
"""
    task, report = _compile_report(source, schema)
    assert report.status is VerificationStatus.COUNTEREXAMPLE

    replay = replay_verification_report(
        report,
        task=task,
        schema=schema,
        model=model,
        tolerance=1e-9,
    )

    assert replay.assertion_satisfied is False
    assert replay.expected_assertion_satisfied is False
    assert replay.is_consistent is True
    point = replay.points["applicant"]
    assert len(point.evaluations) == 1
    evaluation = point.evaluations[0]
    assert evaluation.formal_label == evaluation.model_label == 0
    assert evaluation.label_matches is True
    probability_errors = tuple(evaluation.probability_errors.values())
    quantity_errors = tuple(evaluation.quantity_errors.values())
    assert all(error is not None for error in probability_errors)
    assert all(error is not None for error in quantity_errors)
    assert max(error for error in probability_errors if error is not None) < 1e-9
    assert max(error for error in quantity_errors if error is not None) < 1e-9
    assert "probability(0)" in replay.to_text()
    assert "Evaluation decision" in replay.to_text()
    assert "model_evaluations" in replay.to_record()


def test_witness_replay_reevaluates_original_probability_intent(tmp_path) -> None:
    model, schema = _artifacts(tmp_path)
    source = """
model := "binary.joblib"
target := decision

[LOGIC]:
exists applicant
with domain(applicant.income: [1.0, 3.0])
=> target[applicant].probability(1) >= 0.5 using Z3
"""
    task, report = _compile_report(source, schema)
    assert report.status is VerificationStatus.WITNESS

    replay = replay_verification_report(
        report,
        task=task,
        schema=schema,
        model=model,
    )

    assert replay.assertion_satisfied is True
    assert replay.expected_assertion_satisfied is True
    assert replay.is_consistent is True


def test_multi_point_classification_replay_preserves_each_evaluation(tmp_path) -> None:
    model, schema = _artifacts(tmp_path)
    source = """
model := "binary.joblib"
target := decision

[LOGIC]:
exists left, right
with domain(
    left.income: [-3.0, -1.0],
    right.income: [1.0, 3.0]
)
=> target[left].label == 0 and
   target[right].probability(1) >= 0.5 using Z3
"""
    task, report = _compile_report(source, schema)
    assert report.status is VerificationStatus.WITNESS
    assert len(report.model_evaluations) == 2

    replay = replay_verification_report(
        report,
        task=task,
        schema=schema,
        model=model,
    )

    assert tuple(replay.points) == ("left", "right")
    assert len(replay.points["left"].evaluations) == 1
    assert len(replay.points["right"].evaluations) == 1
    assert replay.points["left"].evaluations[0].formal_label == 0
    assert replay.points["right"].evaluations[0].formal_label == 1
    assert replay.assertion_satisfied is True
    assert replay.is_consistent is True


@dataclass
class _ProtocolObserver:
    observer_id: str = "protocol-observer"

    def supports(self, *, schema, model: object) -> bool:
        return True

    def observe(
        self,
        *,
        schema,
        model: object,
        inputs: Mapping[str, Any],
    ) -> ModelObservation:
        linear = schema.metadata["linear"]
        decision = float(linear["coef"][0][0]) * float(inputs["income"]) + float(
            linear["intercept"][0]
        )
        probability = 1.0 / (1.0 + __import__("math").exp(-decision))
        return ModelObservation(
            output_name=schema.output_name,
            predicted_label=1 if decision > 0 else 0,
            class_probabilities={0: 1.0 - probability, 1: probability},
            model_quantities={"oriented_decision_value": decision},
        )


def test_replay_accepts_custom_observer_protocol_instead_of_estimator_type(
    tmp_path,
) -> None:
    _model, schema = _artifacts(tmp_path)
    source = """
model := "binary.joblib"
target := decision

[LOGIC]:
exists applicant
with domain(applicant.income: [1.0, 1.0])
=> target[applicant].label == 1 using Z3
"""
    task, report = _compile_report(source, schema)

    replay = replay_verification_report(
        report,
        task=task,
        schema=schema,
        model=object(),
        observer_registry=ModelObserverRegistry((_ProtocolObserver(),)),
    )

    assert replay.is_consistent is True


@dataclass
class _MismatchingObserver:
    observer_id: str = "mismatching-observer"

    def supports(self, *, schema, model: object) -> bool:
        return True

    def observe(
        self,
        *,
        schema,
        model: object,
        inputs: Mapping[str, Any],
    ) -> ModelObservation:
        return ModelObservation(
            output_name=schema.output_name,
            predicted_label=0,
            class_probabilities={0: 0.9, 1: 0.1},
            model_quantities={"oriented_decision_value": -2.0},
        )


def test_replay_detects_concrete_classification_mismatch(tmp_path) -> None:
    _model, schema = _artifacts(tmp_path)
    source = """
model := "binary.joblib"
target := decision

[LOGIC]:
exists applicant
with domain(applicant.income: [1.0, 1.0])
=> target[applicant].label == 1 using Z3
"""
    task, report = _compile_report(source, schema)

    replay = replay_verification_report(
        report,
        task=task,
        schema=schema,
        model=object(),
        observer_registry=ModelObserverRegistry((_MismatchingObserver(),)),
    )

    assert replay.assertion_satisfied is False
    assert replay.expected_assertion_satisfied is True
    assert replay.is_consistent is False


def test_finding_replay_accepts_custom_observer_registry(tmp_path) -> None:
    _model, schema = _artifacts(tmp_path)
    source = """
model := "binary.joblib"
target := decision

[LOGIC]:
exists applicant
with domain(applicant.income: [1.0, 1.0])
=> target[applicant].label == 1 using Z3
"""
    task, report = _compile_report(source, schema)
    finding = VerificationFinding(report=report, task=task, schema=schema)

    replay = finding.replay(
        object(),
        observer_registry=ModelObserverRegistry((_ProtocolObserver(),)),
    )

    assert replay.is_consistent is True
