from __future__ import annotations

from dsl.ast.nodes.base import ASTNode
from dsl.ast.nodes.outputs import (
    ClassProbabilityObservableNode,
    ModelOutputRefNode,
    OutputObservableNode,
    PredictedLabelObservableNode,
)
from dsl.ast.nodes.primitives import ConstantNode, ScalarExpressionNode
from dsl.language.vocabulary.outputs import EnumOutputSelector
from dsl.semantic.types.enums import EnumDataType


def test_ast_obs_001_output_reference_is_not_a_scalar_expression() -> None:
    output = ModelOutputRefNode(point="x0")

    assert isinstance(output, ASTNode)
    assert not isinstance(output, ScalarExpressionNode)
    assert output.point == "x0"
    assert output.name == "target"


def test_ast_obs_001_predicted_label_is_an_explicit_scalar_projection() -> None:
    output = ModelOutputRefNode(point="x0")
    observable = PredictedLabelObservableNode(output=output)

    assert isinstance(observable, OutputObservableNode)
    assert isinstance(observable, ScalarExpressionNode)
    assert observable.output is output
    assert observable.observable is EnumOutputSelector.LABEL


def test_ast_obs_001_class_probability_keeps_explicit_label() -> None:
    output = ModelOutputRefNode(point="x0")
    label = ConstantNode(value="approved", dtype=EnumDataType.STRING)
    observable = ClassProbabilityObservableNode(output=output, label=label)

    assert isinstance(observable, OutputObservableNode)
    assert isinstance(observable, ScalarExpressionNode)
    assert observable.output is output
    assert observable.label is label
    assert observable.observable is EnumOutputSelector.PROBABILITY
