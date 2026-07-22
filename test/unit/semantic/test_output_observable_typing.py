from __future__ import annotations

import pytest

from dsl.ast.nodes.assertion import ComparisonNode
from dsl.ast.nodes.outputs import (
    ClassProbabilityObservableNode,
    PredictedLabelObservableNode,
)
from dsl.builder.program import parse_program
from dsl.parser.errors import ParserError
from dsl.parser.parser import parse_forml_code
from dsl.semantic.core.validator import FORMLValidator
from dsl.semantic.runtime.tracer import ValidationTracer
from dsl.semantic.types.enums import EnumDataType
from model.detector.model_framework import EnumModelFramework
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema
from model.schema.output_schema import ClassificationOutputSchema


def _schema(label_dtype: EnumDataType, labels) -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LogisticRegression",
        features={"age": FeatureSchema("age", EnumDataType.INT)},
        output_name="MyTarget",
        task="classification",
        output_schema=ClassificationOutputSchema(
            label_dtype=label_dtype,
            labels=tuple(labels),
            probability_available=True,
        ),
    )


def _program(assertion: str):
    return parse_program(parse_forml_code(f"""
        model := "model.pkl"
        target := MyTarget

        [LOGIC]:
        forall x0 => {assertion}
        """))


@pytest.mark.parametrize(
    "label_dtype, labels, literal",
    [
        pytest.param(EnumDataType.STRING, ("no", "yes"), '"yes"', id="string"),
        pytest.param(EnumDataType.INT, (0, 1), "1", id="integer"),
        pytest.param(EnumDataType.FLOAT, (-1.5, 1.5), "1.5", id="float"),
        pytest.param(EnumDataType.BOOL, (False, True), "true", id="boolean"),
    ],
)
def test_sem_obs_001_label_observable_uses_schema_label_dtype(
    label_dtype: EnumDataType,
    labels,
    literal: str,
) -> None:
    program = _program(f"target[x0].label == {literal}")
    FORMLValidator().validate(
        program,
        tracer=ValidationTracer(enabled=False),
        model_schema=_schema(label_dtype, labels),
    )
    comparison = program.body[0].rule.assertion.root
    assert isinstance(comparison, ComparisonNode)
    assert isinstance(comparison.left, PredictedLabelObservableNode)
    assert comparison.left.semantic is not None
    assert comparison.left.semantic.inferred_dtype is label_dtype
    assert comparison.left.semantic.arithmetic_allowed is False
    assert comparison.left.semantic.ordering_allowed is False


def test_sem_obs_002_probability_is_float_typed() -> None:
    program = _program('target[x0].probability("yes") >= 0.8')
    FORMLValidator().validate(
        program,
        tracer=ValidationTracer(enabled=False),
        model_schema=_schema(EnumDataType.STRING, ("no", "yes")),
    )
    comparison = program.body[0].rule.assertion.root
    assert isinstance(comparison, ComparisonNode)
    assert isinstance(comparison.left, ClassProbabilityObservableNode)
    assert comparison.left.semantic is not None
    assert comparison.left.semantic.inferred_dtype is EnumDataType.FLOAT
    assert comparison.left.semantic.arithmetic_allowed is True
    assert comparison.left.semantic.ordering_allowed is True


@pytest.mark.parametrize(
    "assertion, message, schema",
    [
        pytest.param(
            'target[x0].label + 1 == "yes"',
            "Predicted labels cannot participate in arithmetic",
            _schema(EnumDataType.STRING, ("no", "yes")),
            id="arithmetic",
        ),
        pytest.param(
            'target[x0].label > "yes"',
            "Ordering comparisons are not defined for predicted labels",
            _schema(EnumDataType.STRING, ("no", "yes")),
            id="ordering-string",
        ),
        pytest.param(
            "target[x0].label >= 1",
            "Ordering comparisons are not defined for predicted labels",
            _schema(EnumDataType.INT, (0, 1)),
            id="ordering-numeric",
        ),
    ],
)
def test_sem_obs_006_rejects_arithmetic_and_ordering_on_labels(
    assertion: str,
    message: str,
    schema: ModelSchema,
) -> None:
    with pytest.raises(ParserError, match=message):
        FORMLValidator().validate(
            _program(assertion),
            tracer=ValidationTracer(enabled=False),
            model_schema=schema,
        )
