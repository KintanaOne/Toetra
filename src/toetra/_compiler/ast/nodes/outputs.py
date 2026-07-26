from __future__ import annotations

from dataclasses import dataclass

from toetra._compiler.ast.nodes.base import ASTNode
from toetra._compiler.ast.nodes.primitives import ConstantNode, ScalarExpressionNode
from toetra._language.vocabulary.outputs import EnumOutputSelector


@dataclass
class ModelOutputRefNode(ASTNode):
    """Reference to the declared model-output port at one evaluation point.

    Unlike the historical :class:`TargetRefNode`, this node does not claim that
    the referenced output is directly scalar-valued. A public observable must
    be selected before it can participate in a scalar comparison.
    """

    point: str | None = None
    name: str = "target"


class OutputObservableNode(ScalarExpressionNode):
    """Base class for a scalar observable projected from a model output."""

    output: ModelOutputRefNode


@dataclass
class PredictedLabelObservableNode(OutputObservableNode):
    """Declarative reference to the label predicted for one evaluation."""

    output: ModelOutputRefNode

    @property
    def observable(self) -> EnumOutputSelector:
        return EnumOutputSelector.LABEL


@dataclass
class ClassProbabilityObservableNode(OutputObservableNode):
    """Declarative probability estimate for one explicit class label."""

    output: ModelOutputRefNode
    label: ConstantNode

    @property
    def observable(self) -> EnumOutputSelector:
        return EnumOutputSelector.PROBABILITY
