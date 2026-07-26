from __future__ import annotations

from toetra._compiler.ast.nodes.assertion import ComparisonNode
from toetra._compiler.ast.nodes.outputs import (
    ClassProbabilityObservableNode,
    PredictedLabelObservableNode,
)
from tests.support.program_builder import build_program


def test_output_observable_surface_builds_both_public_forms() -> None:
    label_program = build_program(body='forall x0 => target[x0].label == "approved"')
    probability_program = build_program(
        body='forall x0 => target[x0].probability("approved") >= 0.8'
    )

    label_root = label_program.body[0].rule.assertion.root
    probability_root = probability_program.body[0].rule.assertion.root

    assert isinstance(label_root, ComparisonNode)
    assert isinstance(label_root.left, PredictedLabelObservableNode)
    assert isinstance(probability_root, ComparisonNode)
    assert isinstance(probability_root.left, ClassProbabilityObservableNode)
