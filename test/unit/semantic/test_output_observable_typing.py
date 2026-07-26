from __future__ import annotations

import pytest

from toetra._compiler.ast.nodes.assertion import ComparisonNode
from toetra._compiler.ast.nodes.outputs import (
    ClassProbabilityObservableNode,
    PredictedLabelObservableNode,
)
from toetra._compiler.builder.program import parse_program
from toetra._compiler.parser.errors import ParserError
from toetra._compiler.parser.parser import parse_toetra_code
from toetra._compiler.semantic.core.validator import ToetraValidator
from toetra._compiler.semantic.runtime.tracer import ValidationTracer
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.schema.output_schema import ClassificationOutputSchema


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
    return parse_program(parse_toetra_code(f"""
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
    ToetraValidator().validate(
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
    ToetraValidator().validate(
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
        ToetraValidator().validate(
            _program(assertion),
            tracer=ValidationTracer(enabled=False),
            model_schema=schema,
        )
