from __future__ import annotations

import pytest

from toetra._compiler.ir.ir1.model_quantities import (
    EnumModelQuantityKind,
    ModelQuantityExpressionIR,
)
from toetra._compiler.ir.ir1.nodes import ComparisonIR, ConstantExpressionIR
from toetra._compiler.ir.ir1.run_ir1 import run_ir
from toetra._language.vocabulary.operators import EnumComparisonOperator
from toetra._models.semantics.evidence import LoweringEvidence
from toetra._models.semantics.lowering import ModelSemanticLowerer
from tests.support.model_semantics import (
    label_property,
    make_binary_logistic_schema,
)


@pytest.mark.parametrize(
    ("label", "operator", "canonical_operator"),
    [
        ("approved", "==", EnumComparisonOperator.GT),
        ("rejected", "==", EnumComparisonOperator.LTE),
        ("approved", "!=", EnumComparisonOperator.LTE),
        ("rejected", "!=", EnumComparisonOperator.GT),
    ],
)
def test_binary_label_literal_is_lowered_to_exact_boundary_constraint(
    label: str,
    operator: str,
    canonical_operator: EnumComparisonOperator,
) -> None:
    schema = make_binary_logistic_schema()
    task = run_ir(label_property(label=label, operator=operator), model_schema=schema)[
        0
    ]

    lowered = ModelSemanticLowerer().lower_task(task, schema=schema)

    comparison = lowered.task.query.expression
    assert isinstance(comparison, ComparisonIR)
    assert isinstance(comparison.left, ModelQuantityExpressionIR)
    assert (
        comparison.left.quantity_kind is EnumModelQuantityKind.ORIENTED_DECISION_VALUE
    )
    assert comparison.op is canonical_operator
    assert isinstance(comparison.right, ConstantExpressionIR)
    assert comparison.right.value == 0
    assert len(lowered.evidence) == 1


def test_label_orientation_depends_on_order_not_spelling() -> None:
    schema = make_binary_logistic_schema(labels=("approved", "rejected"))
    task = run_ir(
        label_property(label="rejected"),
        model_schema=schema,
    )[0]

    lowered = ModelSemanticLowerer().lower_task(task, schema=schema)

    comparison = lowered.task.query.expression
    assert isinstance(comparison, ComparisonIR)
    assert comparison.op is EnumComparisonOperator.GT
    evidence = lowered.evidence[0]
    assert isinstance(evidence, LoweringEvidence)
    assert evidence.boundary_policy.equality_label == "approved"


def test_observable_may_appear_on_right_without_changing_semantics() -> None:
    schema = make_binary_logistic_schema()
    task = run_ir(
        label_property(observable_on_left=False),
        model_schema=schema,
    )[0]

    lowered = ModelSemanticLowerer().lower_task(task, schema=schema)

    comparison = lowered.task.query.expression
    assert isinstance(comparison, ComparisonIR)
    assert comparison.op is EnumComparisonOperator.GT
    evidence = lowered.evidence[0]
    assert isinstance(evidence, LoweringEvidence)
    assert evidence.source_intent.observable_on_left is False
