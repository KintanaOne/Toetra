from __future__ import annotations

from dsl.backends.execution import (
    BackendExecutionEvidence,
    BackendExecutionPolicy,
    BackendExecutionStatus,
    BackendResourceLimits,
)
from dsl.backends.results import VerificationResult, VerificationStatus
from dsl.language.vocabulary.backends import EnumBackend
from dsl.runtime import BackendRunnerRegistry, verify
from dsl.semantic.types.enums import EnumDataType
from model.detector.model_framework import EnumModelFramework
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema

_SOURCE = """
model := "model.joblib"
target := score

[LOGIC]:
forall x0
    with domain(x0.a: [0.0, 3.0])
    => target <= 7.0
    using Z3
"""


def _schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={"a": FeatureSchema(name="a", dtype=EnumDataType.FLOAT)},
        target="score",
        task="regression",
        target_dtype=EnumDataType.FLOAT,
        metadata={
            "linear": {
                "coef": [2.0],
                "intercept": 1.0,
                "feature_names": ["a"],
            }
        },
    )


def test_verify_applies_one_generic_policy_to_routing_execution_and_reporting() -> None:
    policy = BackendExecutionPolicy(
        timeout_ms=2_500,
        resources=BackendResourceLimits(max_backend_units=100_000),
        deterministic_seed=5,
    )

    session = verify(_SOURCE, schema=_schema(), execution_policy=policy)
    report = session.reports[0]

    assert report.backend_execution is not None
    assert report.backend_execution.status in {"sat", "unsat"}
    assert report.backend_execution.timeout_ms == 2_500
    assert report.backend_execution.max_backend_units == 100_000
    assert report.backend_execution.deterministic_seed == 5
    assert report.backend_execution.duration_ms >= 0
    record = session.to_records()[0]
    assert record["backend_execution_status"] in {"sat", "unsat"}
    assert record["backend_timeout_ms"] == 2_500


class _CapturingRunner:
    def __init__(self) -> None:
        self.policy: BackendExecutionPolicy | None = None

    def run(self, task, *, policy: BackendExecutionPolicy | None = None):
        del task
        assert policy is not None
        self.policy = policy
        return VerificationResult(
            status=VerificationStatus.UNKNOWN,
            backend=EnumBackend.Z3,
            backend_status="custom_unknown",
            message="custom backend was inconclusive",
            execution=BackendExecutionEvidence(
                status=BackendExecutionStatus.UNKNOWN,
                duration_ms=1.25,
                policy=policy.snapshot(),
                reason="custom reason",
                backend_reason="adapter detail",
            ),
        )


def test_custom_runner_receives_the_same_backend_neutral_contract() -> None:
    runner = _CapturingRunner()
    registry = BackendRunnerRegistry()
    registry.register(EnumBackend.Z3, runner)
    policy = BackendExecutionPolicy(timeout_ms=900)

    session = verify(
        _SOURCE,
        schema=_schema(),
        runner_registry=registry,
        execution_policy=policy,
    )

    assert runner.policy is policy
    assert session.reports[0].backend_execution is not None
    assert session.reports[0].backend_execution.status == "unknown"
    assert session.reports[0].backend_execution.backend_reason == "adapter detail"
