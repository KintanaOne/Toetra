from __future__ import annotations

import pytest

from toetra._compiler.ast.nodes.assertion import ComparisonNode
from toetra._compiler.ast.nodes.primitives import TargetRefNode
from toetra._compiler.builder.program import parse_program
from toetra._compiler.parser.errors import ParserError
from toetra._compiler.parser.parser import parse_toetra_code
from toetra._compiler.semantic.core.validator import ToetraValidator
from toetra._compiler.semantic.runtime.tracer import ValidationTracer
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.schema.output_schema import (
    ClassificationOutputSchema,
    RegressionOutputSchema,
)


def _classification_schema(*, probability_available: bool = True) -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LogisticRegression",
        features={"age": FeatureSchema("age", EnumDataType.INT)},
        output_name="MyTarget",
        task="classification",
        output_schema=ClassificationOutputSchema(
            label_dtype=EnumDataType.STRING,
            labels=("rejected", "approved"),
            probability_available=probability_available,
        ),
    )


def _regression_schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={"age": FeatureSchema("age", EnumDataType.INT)},
        output_name="MyTarget",
        task="regression",
        output_schema=RegressionOutputSchema(value_dtype=EnumDataType.FLOAT),
    )


def _program(assertion: str, *, target: str = "MyTarget"):
    return parse_program(parse_toetra_code(f"""
        model := "model.pkl"
        target := {target}

        [LOGIC]:
        forall x0 => {assertion}
        """))


def test_sem_obs_003_rejects_unknown_probability_label() -> None:
    with pytest.raises(ParserError, match="Unknown classification label 'unknown'"):
        ToetraValidator().validate(
            _program('target[x0].probability("unknown") >= 0.8'),
            tracer=ValidationTracer(enabled=False),
            model_schema=_classification_schema(),
        )


def test_sem_obs_003_rejects_wrong_typed_probability_label() -> None:
    with pytest.raises(
        ParserError,
        match="Probability label has incompatible type: expected string, got int",
    ):
        ToetraValidator().validate(
            _program("target[x0].probability(1) >= 0.8"),
            tracer=ValidationTracer(enabled=False),
            model_schema=_classification_schema(),
        )


def test_sem_obs_003_uses_type_safe_label_identity() -> None:
    schema = ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LogisticRegression",
        features={"age": FeatureSchema("age", EnumDataType.INT)},
        output_name="MyTarget",
        task="classification",
        output_schema=ClassificationOutputSchema(
            label_dtype=EnumDataType.BOOL,
            labels=(False, True),
            probability_available=True,
        ),
    )
    with pytest.raises(ParserError, match="expected bool, got int"):
        ToetraValidator().validate(
            _program("target[x0].probability(1) >= 0.8"),
            tracer=ValidationTracer(enabled=False),
            model_schema=schema,
        )


def test_sem_obs_004_rejects_bare_classification_target_as_ambiguous() -> None:
    with pytest.raises(
        ParserError,
        match="classification output requires an explicit observable",
    ):
        ToetraValidator().validate(
            _program("target[x0] == 1"),
            tracer=ValidationTracer(enabled=False),
            model_schema=_classification_schema(),
        )


def test_sem_obs_005_retains_bare_scalar_regression_target() -> None:
    program = _program("target[x0] <= 1.0")
    assert ToetraValidator().validate(
        program,
        tracer=ValidationTracer(enabled=False),
        model_schema=_regression_schema(),
    )
    comparison = program.body[0].rule.assertion.root
    assert isinstance(comparison, ComparisonNode)
    assert isinstance(comparison.left, TargetRefNode)
    assert comparison.left.semantic is not None
    assert comparison.left.semantic.inferred_dtype is EnumDataType.FLOAT


@pytest.mark.parametrize(
    "assertion, requested",
    [
        pytest.param(
            'target[x0].label == "approved"',
            "predicted label",
            id="label",
        ),
        pytest.param(
            'target[x0].probability("approved") >= 0.8',
            "class probability",
            id="probability",
        ),
    ],
)
def test_sem_obs_007_rejects_classification_observables_on_regression(
    assertion: str,
    requested: str,
) -> None:
    with pytest.raises(
        ParserError,
        match=rf"Cannot access {requested} on a regression model output",
    ):
        ToetraValidator().validate(
            _program(assertion),
            tracer=ValidationTracer(enabled=False),
            model_schema=_regression_schema(),
        )


def test_probability_observable_requires_model_probability_capability() -> None:
    with pytest.raises(ParserError, match="does not expose class probabilities"):
        ToetraValidator().validate(
            _program('target[x0].probability("approved") >= 0.8'),
            tracer=ValidationTracer(enabled=False),
            model_schema=_classification_schema(probability_available=False),
        )


def test_output_reference_rejects_header_schema_name_mismatch() -> None:
    with pytest.raises(
        ParserError,
        match="Declared target does not match the selected model output",
    ):
        ToetraValidator().validate(
            _program('target[x0].label == "approved"', target="OtherTarget"),
            tracer=ValidationTracer(enabled=False),
            model_schema=_classification_schema(),
        )
