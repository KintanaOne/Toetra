from __future__ import annotations

import pytest

import toetra._runtime.api as runtime_api
from tests.support.binary_classification import (
    binary_probability_property,
    make_sklearn_logistic_schema,
)
from toetra import (
    VerificationConfigurationError,
    VerificationRuntimeError,
    verify,
)
from toetra._backends.errors import (
    BackendNotRegisteredError,
    BackendRoutingError,
    NoCompatibleBackendError,
    NumericCompatibilityRouteError,
)
from toetra._backends.registry import BackendRegistry
from toetra._compatibility.errors import (
    AmbiguousCompatibilityRuleError,
    InvalidCompatibilityDescriptorError,
    NumericCompatibilityError,
)
from toetra._compatibility.registry import NumericCompatibilityRegistry
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.encoder.errors import (
    InvalidModelAssumptionError,
    MissingModelParameterError,
    ModelEncoderError,
    UnsupportedModelEncoderError,
    UnsupportedModelParameterError,
)
from toetra._models.ir_builder.errors import (
    MissingModelIRParameterError,
    UnsupportedModelIRBuilderError,
)
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.semantics.errors import (
    InvalidModelSemanticProfileError,
    MissingModelSemanticsError,
    ModelSemanticLoweringError,
    UnsupportedModelSemanticProfileError,
    UnsupportedObservableLoweringError,
)

_SOURCE = """
model := "model.joblib"
target := score

[LOGIC]:
forall x0
    with domain(x0.a: [0.0, 3.0])
    => target <= 7.0
    using Z3
"""


def _schema(
    *,
    model_type: str = "LinearRegression",
    metadata: dict[str, object] | None = None,
    include_second_feature: bool = False,
) -> ModelSchema:
    features = {"a": FeatureSchema(name="a", dtype=EnumDataType.FLOAT)}
    feature_names = ["a"]
    coefficients = [2.0]
    if include_second_feature:
        features["b"] = FeatureSchema(name="b", dtype=EnumDataType.FLOAT)
        feature_names.append("b")
        coefficients.append(1.0)
    if metadata is None:
        metadata = {
            "linear": {
                "coef": coefficients,
                "intercept": 1.0,
                "feature_names": feature_names,
            }
        }
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type=model_type,
        features=features,
        target="score",
        task="regression",
        target_dtype=EnumDataType.FLOAT,
        metadata=metadata,
    )


def test_verify_reports_missing_model_encoder_as_unsupported_route() -> None:
    with pytest.raises(VerificationRuntimeError) as caught:
        verify(_SOURCE, schema=_schema(model_type="DecisionTreeRegressor"))

    error = caught.value
    assert not isinstance(error, VerificationConfigurationError)
    assert error.code == "MODEL_ENCODER_UNSUPPORTED"
    assert error.stage == "model"
    assert error.hint is not None
    assert isinstance(error.__cause__, UnsupportedModelIRBuilderError)


def test_verify_reports_missing_encoder_parameter_as_invalid_configuration() -> None:
    with pytest.raises(VerificationConfigurationError) as caught:
        verify(_SOURCE, schema=_schema(metadata={}))

    error = caught.value
    assert error.code == "MODEL_ENCODER_PARAMETER_MISSING"
    assert error.stage == "model"
    assert error.hint is not None
    assert isinstance(error.__cause__, MissingModelIRParameterError)


def test_verify_reports_unsupported_output_observable_route() -> None:
    with pytest.raises(VerificationRuntimeError) as caught:
        verify(
            binary_probability_property(threshold="1.0"),
            schema=make_sklearn_logistic_schema(),
        )

    error = caught.value
    assert error.code == "MODEL_OBSERVABLE_UNSUPPORTED"
    assert error.stage == "model"
    assert error.hint is not None
    assert isinstance(error.__cause__, UnsupportedObservableLoweringError)


def test_verify_reports_missing_numeric_compatibility_route() -> None:
    with pytest.raises(VerificationRuntimeError) as caught:
        verify(
            _SOURCE,
            schema=_schema(),
            numeric_compatibility_registry=NumericCompatibilityRegistry(),
        )

    error = caught.value
    assert error.code == "NUMERIC_COMPATIBILITY_ROUTE_UNSUPPORTED"
    assert error.stage == "compatibility"
    assert error.hint is not None
    assert isinstance(error.__cause__, NumericCompatibilityRouteError)


def test_verify_reports_unregistered_requested_backend() -> None:
    with pytest.raises(VerificationRuntimeError) as caught:
        verify(
            _SOURCE,
            schema=_schema(),
            backend_registry=BackendRegistry(),
        )

    error = caught.value
    assert error.code == "BACKEND_NOT_REGISTERED"
    assert error.stage == "routing"
    assert error.hint is not None
    assert isinstance(error.__cause__, BackendNotRegisteredError)


def test_verify_reports_structurally_unsupported_backend_route() -> None:
    source = """
model := "model.joblib"
target := score

[LOGIC]:
forall x0 => x0.a * x0.b <= 7.0 using Z3
"""

    with pytest.raises(VerificationRuntimeError) as caught:
        verify(source, schema=_schema(include_second_feature=True))

    error = caught.value
    assert error.code == "BACKEND_ROUTE_UNSUPPORTED"
    assert error.stage == "routing"
    assert error.hint is not None
    assert isinstance(error.__cause__, NoCompatibleBackendError)
    assert not isinstance(error.__cause__, NumericCompatibilityRouteError)


@pytest.mark.parametrize(
    ("private_error", "code"),
    [
        (
            UnsupportedModelEncoderError("unsupported encoder"),
            "MODEL_ENCODER_UNSUPPORTED",
        ),
        (
            MissingModelParameterError("missing parameter"),
            "MODEL_ENCODER_PARAMETER_MISSING",
        ),
        (
            UnsupportedModelParameterError("unsupported parameter"),
            "MODEL_ENCODER_PARAMETER_UNSUPPORTED",
        ),
        (
            InvalidModelAssumptionError("invalid assumptions"),
            "MODEL_ENCODER_OUTPUT_INVALID",
        ),
        (ModelEncoderError("encoding failed"), "MODEL_ENCODING_FAILED"),
    ],
)
def test_verify_normalizes_model_encoder_failures(
    monkeypatch: pytest.MonkeyPatch,
    private_error: ModelEncoderError,
    code: str,
) -> None:
    def reject_route(*_args: object, **_kwargs: object) -> None:
        raise private_error

    monkeypatch.setattr(runtime_api, "run_ir2_with_model_schema", reject_route)
    public_type = (
        VerificationConfigurationError
        if isinstance(private_error, MissingModelParameterError)
        else VerificationRuntimeError
    )

    with pytest.raises(public_type) as caught:
        verify(_SOURCE, schema=_schema())

    error = caught.value
    assert error.code == code
    assert error.stage == "model"
    assert error.hint is not None
    assert error.__cause__ is private_error


@pytest.mark.parametrize(
    ("private_error", "code"),
    [
        (
            UnsupportedModelSemanticProfileError("unsupported profile"),
            "MODEL_SEMANTIC_PROFILE_UNSUPPORTED",
        ),
        (
            UnsupportedObservableLoweringError("unsupported observable"),
            "MODEL_OBSERVABLE_UNSUPPORTED",
        ),
        (
            InvalidModelSemanticProfileError("invalid profile"),
            "MODEL_SEMANTIC_PROFILE_INVALID",
        ),
        (
            MissingModelSemanticsError("incomplete lowering"),
            "MODEL_SEMANTIC_LOWERING_INCOMPLETE",
        ),
        (
            ModelSemanticLoweringError("lowering failed"),
            "MODEL_SEMANTIC_LOWERING_FAILED",
        ),
    ],
)
def test_verify_normalizes_model_semantic_failures(
    monkeypatch: pytest.MonkeyPatch,
    private_error: ModelSemanticLoweringError,
    code: str,
) -> None:
    def reject_route(*_args: object, **_kwargs: object) -> None:
        raise private_error

    monkeypatch.setattr(runtime_api, "run_ir2_with_model_schema", reject_route)

    with pytest.raises(VerificationRuntimeError) as caught:
        verify(_SOURCE, schema=_schema())

    error = caught.value
    assert error.code == code
    assert error.stage == "model"
    assert error.hint is not None
    assert error.__cause__ is private_error


@pytest.mark.parametrize(
    ("private_error", "code"),
    [
        (
            AmbiguousCompatibilityRuleError("ambiguous rules"),
            "NUMERIC_COMPATIBILITY_AMBIGUOUS",
        ),
        (
            InvalidCompatibilityDescriptorError("invalid descriptor"),
            "NUMERIC_COMPATIBILITY_INVALID",
        ),
    ],
)
def test_verify_normalizes_numeric_compatibility_failures(
    monkeypatch: pytest.MonkeyPatch,
    private_error: NumericCompatibilityError,
    code: str,
) -> None:
    def reject_route(*_args: object, **_kwargs: object) -> None:
        raise private_error

    monkeypatch.setattr(runtime_api.BackendRouter, "route", reject_route)

    with pytest.raises(VerificationRuntimeError) as caught:
        verify(_SOURCE, schema=_schema())

    error = caught.value
    assert error.code == code
    assert error.stage == "compatibility"
    assert error.hint is not None
    assert error.__cause__ is private_error


@pytest.mark.parametrize(
    ("private_error", "code"),
    [
        (
            NumericCompatibilityRouteError("unsupported numeric route"),
            "NUMERIC_COMPATIBILITY_ROUTE_UNSUPPORTED",
        ),
        (
            BackendNotRegisteredError("backend not registered"),
            "BACKEND_NOT_REGISTERED",
        ),
        (
            NoCompatibleBackendError("unsupported backend route"),
            "BACKEND_ROUTE_UNSUPPORTED",
        ),
        (BackendRoutingError("routing failed"), "BACKEND_ROUTING_FAILED"),
    ],
)
def test_verify_normalizes_backend_routing_failures(
    monkeypatch: pytest.MonkeyPatch,
    private_error: BackendRoutingError,
    code: str,
) -> None:
    def reject_route(*_args: object, **_kwargs: object) -> None:
        raise private_error

    monkeypatch.setattr(runtime_api.BackendRouter, "route", reject_route)

    with pytest.raises(VerificationRuntimeError) as caught:
        verify(_SOURCE, schema=_schema())

    error = caught.value
    expected_stage = (
        "compatibility"
        if isinstance(private_error, NumericCompatibilityRouteError)
        else "routing"
    )
    assert error.code == code
    assert error.stage == expected_stage
    assert error.hint is not None
    assert error.__cause__ is private_error


def test_verify_does_not_relabel_unexpected_route_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    failure = RuntimeError("unexpected integration failure")

    def reject_route(*_args: object, **_kwargs: object) -> None:
        raise failure

    monkeypatch.setattr(runtime_api, "run_ir2_with_model_schema", reject_route)

    with pytest.raises(RuntimeError) as caught:
        verify(_SOURCE, schema=_schema())

    assert caught.value is failure
    assert not isinstance(caught.value, VerificationRuntimeError)
