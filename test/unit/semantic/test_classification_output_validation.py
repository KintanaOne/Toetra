from __future__ import annotations

import pytest

from dsl.ast.nodes.assertion import ComparisonNode
from dsl.ast.nodes.primitives import TargetRefNode
from dsl.builder.program import parse_program
from dsl.parser.errors import ParserError
from dsl.parser.parser import parse_forml_code
from dsl.semantic.core.validator import FORMLValidator
from dsl.semantic.runtime.tracer import ValidationTracer
from dsl.semantic.types.enums import EnumDataType
from model.detector.model_framework import EnumModelFramework
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema
from model.schema.output_schema import (
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
    return parse_program(parse_forml_code(f"""
        model := "model.pkl"
        target := {target}

        [LOGIC]:
        forall x0 => {assertion}
        """))


def test_sem_obs_003_rejects_unknown_probability_label() -> None:
    with pytest.raises(ParserError, match="Unknown classification label 'unknown'"):
        FORMLValidator().validate(
            _program('target[x0].probability("unknown") >= 0.8'),
            tracer=ValidationTracer(enabled=False),
            model_schema=_classification_schema(),
        )


def test_sem_obs_003_rejects_wrong_typed_probability_label() -> None:
    with pytest.raises(
        ParserError,
        match="Probability label has incompatible type: expected string, got int",
    ):
        FORMLValidator().validate(
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
        FORMLValidator().validate(
            _program("target[x0].probability(1) >= 0.8"),
            tracer=ValidationTracer(enabled=False),
            model_schema=schema,
        )


def test_sem_obs_004_rejects_bare_classification_target_as_ambiguous() -> None:
    with pytest.raises(
        ParserError,
        match="classification output requires an explicit observable",
    ):
        FORMLValidator().validate(
            _program("target[x0] == 1"),
            tracer=ValidationTracer(enabled=False),
            model_schema=_classification_schema(),
        )


def test_sem_obs_005_retains_bare_scalar_regression_target() -> None:
    program = _program("target[x0] <= 1.0")
    assert FORMLValidator().validate(
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
        FORMLValidator().validate(
            _program(assertion),
            tracer=ValidationTracer(enabled=False),
            model_schema=_regression_schema(),
        )


def test_probability_observable_requires_model_probability_capability() -> None:
    with pytest.raises(ParserError, match="does not expose class probabilities"):
        FORMLValidator().validate(
            _program('target[x0].probability("approved") >= 0.8'),
            tracer=ValidationTracer(enabled=False),
            model_schema=_classification_schema(probability_available=False),
        )


def test_output_reference_rejects_header_schema_name_mismatch() -> None:
    with pytest.raises(
        ParserError,
        match="Declared target does not match the selected model output",
    ):
        FORMLValidator().validate(
            _program('target[x0].label == "approved"', target="OtherTarget"),
            tracer=ValidationTracer(enabled=False),
            model_schema=_classification_schema(),
        )
