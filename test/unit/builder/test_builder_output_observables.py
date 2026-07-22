from __future__ import annotations

import pytest

from dsl.ast.nodes.assertion import ComparisonNode
from dsl.ast.nodes.outputs import (
    ClassProbabilityObservableNode,
    ModelOutputRefNode,
    PredictedLabelObservableNode,
)
from dsl.ast.nodes.primitives import ConstantNode
from dsl.language.vocabulary.outputs import EnumOutputSelector
from dsl.semantic.types.enums import EnumDataType
from test.unit.builder._point_binding_helpers import build_program


def _comparison(body: str) -> ComparisonNode:
    root = build_program(body=body).body[0].rule.assertion.root
    assert isinstance(root, ComparisonNode)
    return root


def test_ast_obs_002_builder_preserves_indexed_label_observable() -> None:
    comparison = _comparison('forall x0 => target[x0].label == "approved"')

    assert isinstance(comparison.left, PredictedLabelObservableNode)
    assert comparison.left == PredictedLabelObservableNode(
        output=ModelOutputRefNode(point="x0")
    )
    assert comparison.left.observable is EnumOutputSelector.LABEL
    assert comparison.left.source_span is not None
    assert comparison.left.output.source_span is not None
    assert comparison.left.source_span.line == comparison.left.output.source_span.line
    assert (
        comparison.left.source_span.column == comparison.left.output.source_span.column
    )
    assert (
        comparison.left.source_span.end_column - comparison.left.source_span.column
        == len("target[x0].label")
    )
    assert (
        comparison.left.output.source_span.end_column
        - comparison.left.output.source_span.column
        == len("target[x0]")
    )


def test_ast_obs_002_builder_preserves_probability_label_and_provenance() -> None:
    comparison = _comparison(
        'forall applicant => target[applicant].probability("approved") >= 0.8'
    )

    assert isinstance(comparison.left, ClassProbabilityObservableNode)
    assert comparison.left.output == ModelOutputRefNode(point="applicant")
    assert comparison.left.label == ConstantNode(
        value="approved",
        dtype=EnumDataType.STRING,
        source_lexeme='"approved"',
    )
    assert comparison.left.observable is EnumOutputSelector.PROBABILITY
    assert comparison.left.source_span is not None
    assert comparison.left.output.source_span is not None
    assert comparison.left.label.source_span is not None
    assert comparison.left.source_span.line == comparison.left.output.source_span.line
    assert comparison.left.source_span.line == comparison.left.label.source_span.line
    assert (
        comparison.left.source_span.column == comparison.left.output.source_span.column
    )
    assert (
        comparison.left.source_span.end_column - comparison.left.source_span.column
        == len('target[applicant].probability("approved")')
    )
    assert (
        comparison.left.output.source_span.end_column
        - comparison.left.output.source_span.column
        == len("target[applicant]")
    )
    assert (
        comparison.left.label.source_span.end_column
        - comparison.left.label.source_span.column
        == len('"approved"')
    )


@pytest.mark.parametrize(
    "label, expected_value, expected_dtype",
    [
        pytest.param('"approved"', "approved", EnumDataType.STRING, id="string"),
        pytest.param("1", 1, EnumDataType.INT, id="integer"),
        pytest.param("-1", -1, EnumDataType.INT, id="negative-integer"),
        pytest.param("-1.5", -1.5, EnumDataType.FLOAT, id="negative-float"),
        pytest.param("true", True, EnumDataType.BOOL, id="boolean"),
    ],
)
def test_ast_obs_002_builder_preserves_literal_label_type(
    label: str,
    expected_value: str | int | float | bool,
    expected_dtype: EnumDataType,
) -> None:
    comparison = _comparison(f"forall x0 => target[x0].probability({label}) >= 0.8")

    assert isinstance(comparison.left, ClassProbabilityObservableNode)
    assert comparison.left.label.value == expected_value
    assert comparison.left.label.dtype is expected_dtype
