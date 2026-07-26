from __future__ import annotations

from lark import Token, Tree

from toetra._compiler.ast.nodes.outputs import (
    ClassProbabilityObservableNode,
    ModelOutputRefNode,
    OutputObservableNode,
    PredictedLabelObservableNode,
)
from toetra._compiler.builder.core.ast_utils import node_value, parse_literal_value
from toetra._compiler.builder.core.source import with_source_span
from toetra._compiler.builder.core.strict import require_node
from toetra._compiler.builder.core.utils import find_node


def parse_model_output_ref(node: Tree) -> ModelOutputRefNode:
    """Build a non-scalar reference to the declared model-output port."""
    output_node = require_node(
        find_node(node, "model_output_ref"),
        "model_output_ref node not found",
    )
    identifier = find_node(output_node, "identifier")
    point = node_value(identifier) if identifier is not None else None
    return with_source_span(ModelOutputRefNode(point=point), output_node)


def parse_output_observable(node: Tree) -> OutputObservableNode:
    """Build one explicit public observable from an output reference."""
    observable_node = require_node(
        find_node(node, "output_observable"),
        "output_observable node not found",
    )
    output = parse_model_output_ref(observable_node)

    label_node = find_node(observable_node, "predicted_label_observable")
    if label_node is not None:
        return with_source_span(
            PredictedLabelObservableNode(output=output),
            observable_node,
        )

    probability_node = find_node(observable_node, "class_probability_observable")
    if probability_node is not None:
        label_node = require_node(
            find_node(probability_node, "class_label_literal"),
            "Class probability requires one literal class label",
        )
        tokens = [
            str(token)
            for token in label_node.scan_values(lambda value: isinstance(value, Token))
        ]
        if not tokens:
            raise ValueError("Class probability requires one literal class label")
        label = with_source_span(parse_literal_value("".join(tokens)), label_node)
        if label.value is None:
            raise ValueError("Class probability label cannot be null")
        return with_source_span(
            ClassProbabilityObservableNode(output=output, label=label),
            observable_node,
        )

    raise ValueError("Unsupported output observable")
