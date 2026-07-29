from __future__ import annotations

import pytest

from toetra import (
    VerificationConfigurationError,
    VerificationRuntimeError,
    verify,
)
from toetra._backends.errors import (
    BackendExecutionError,
    BackendExecutionPolicyError,
    BackendSymbolCollisionError,
    BackendTranslationError,
    UnsupportedBackendRequirementsError,
    UnsupportedScalarExpressionError,
)
from toetra._backends.execution import (
    BackendExecutionEvidence,
    BackendExecutionPolicy,
    BackendExecutionStatus,
)
from toetra._backends.results import VerificationResult
from toetra._compiler.ir.ir2.dsl.nodes import VerificationTaskIR2
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._language.vocabulary.backends import EnumBackend
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema
from toetra._runtime.backends import BackendRunnerRegistry
from toetra._runtime.errors import BackendRunnerNotRegisteredError

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


class _RaisingRunner:
    def __init__(self, error: Exception) -> None:
        self.error = error

    def run(
        self,
        task: VerificationTaskIR2,
        *,
        policy: BackendExecutionPolicy | None = None,
    ) -> VerificationResult:
        del task, policy
        raise self.error


def _runner_registry(error: Exception) -> BackendRunnerRegistry:
    registry = BackendRunnerRegistry()
    registry.register(EnumBackend.Z3, _RaisingRunner(error))
    return registry


def test_verify_normalizes_missing_backend_runner() -> None:
    with pytest.raises(VerificationRuntimeError) as caught:
        verify(
            _SOURCE,
            schema=_schema(),
            runner_registry=BackendRunnerRegistry(),
        )

    error = caught.value
    assert error.code == "BACKEND_RUNNER_NOT_REGISTERED"
    assert error.stage == "backend"
    assert error.hint is not None
    assert isinstance(error.__cause__, BackendRunnerNotRegisteredError)


@pytest.mark.parametrize(
    ("private_error", "code"),
    [
        (
            UnsupportedBackendRequirementsError("requirements unsupported"),
            "BACKEND_TRANSLATION_REQUIREMENTS_UNSUPPORTED",
        ),
        (
            UnsupportedScalarExpressionError("scalar unsupported"),
            "BACKEND_SCALAR_EXPRESSION_UNSUPPORTED",
        ),
        (
            BackendSymbolCollisionError("symbol collision"),
            "BACKEND_SYMBOL_COLLISION",
        ),
        (
            BackendTranslationError("translation failed"),
            "BACKEND_TRANSLATION_FAILED",
        ),
    ],
)
def test_verify_normalizes_backend_translation_failures(
    private_error: BackendTranslationError,
    code: str,
) -> None:
    with pytest.raises(VerificationRuntimeError) as caught:
        verify(
            _SOURCE,
            schema=_schema(),
            runner_registry=_runner_registry(private_error),
        )

    error = caught.value
    assert error.code == code
    assert error.stage == "backend"
    assert error.hint is not None
    assert error.__cause__ is private_error


def test_verify_normalizes_backend_execution_policy_failure() -> None:
    private_error = BackendExecutionPolicyError("invalid backend policy")

    with pytest.raises(VerificationConfigurationError) as caught:
        verify(
            _SOURCE,
            schema=_schema(),
            runner_registry=_runner_registry(private_error),
        )

    error = caught.value
    assert error.code == "BACKEND_EXECUTION_POLICY_INVALID"
    assert error.stage == "backend"
    assert error.hint is not None
    assert error.__cause__ is private_error


def test_verify_normalizes_reserved_z3_execution_option() -> None:
    policy = BackendExecutionPolicy(backend_options={"timeout": 1})

    with pytest.raises(VerificationConfigurationError) as caught:
        verify(_SOURCE, schema=_schema(), execution_policy=policy)

    error = caught.value
    assert error.code == "BACKEND_EXECUTION_POLICY_INVALID"
    assert error.stage == "backend"
    assert isinstance(error.__cause__, BackendExecutionPolicyError)


def test_verify_normalizes_technical_backend_execution_failure() -> None:
    policy = BackendExecutionPolicy()
    private_error = BackendExecutionError(
        "backend failed",
        backend=EnumBackend.Z3.value,
        evidence=BackendExecutionEvidence(
            status=BackendExecutionStatus.ERROR,
            duration_ms=1.0,
            policy=policy.snapshot(),
            reason="technical failure",
            backend_reason="RuntimeError",
        ),
    )

    with pytest.raises(VerificationRuntimeError) as caught:
        verify(
            _SOURCE,
            schema=_schema(),
            runner_registry=_runner_registry(private_error),
        )

    error = caught.value
    assert error.code == "BACKEND_EXECUTION_FAILED"
    assert error.stage == "backend"
    assert error.hint is not None
    assert error.__cause__ is private_error
    assert private_error.evidence.status is BackendExecutionStatus.ERROR


def test_verify_does_not_relabel_unexpected_runner_failure() -> None:
    failure = RuntimeError("unexpected runner failure")

    with pytest.raises(RuntimeError) as caught:
        verify(
            _SOURCE,
            schema=_schema(),
            runner_registry=_runner_registry(failure),
        )

    assert caught.value is failure
    assert not isinstance(caught.value, VerificationRuntimeError)
