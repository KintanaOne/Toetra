from __future__ import annotations

import pytest

from toetra._compiler.ir.ir1.model_quantities import ModelQuantityExpressionIR
from toetra._compiler.ir.ir1.nodes import AndIR, ComparisonIR, OrIR, ProblemIR
from toetra._compiler.ir.ir1.run_ir1 import run_ir
from toetra._language.vocabulary.operators import EnumComparisonOperator
from toetra._models.semantics.errors import UnsupportedObservableLoweringError
from toetra._models.semantics.evidence import PairwiseLoweringEvidence
from toetra._models.semantics.lowering import ModelSemanticLowerer
from tests.support.model_semantics import make_binary_logistic_schema


def _source(assertion: str) -> str:
    return f"""\
model := "credit.joblib"
target := decision

[LOGIC]:
forall left, right => {assertion}
"""


def _lower(assertion: str):
    schema = make_binary_logistic_schema()
    task = run_ir(_source(assertion), model_schema=schema)[0]
    return ModelSemanticLowerer().lower_task(task, schema=schema)


def _branch_signature(expression: OrIR) -> tuple[tuple[tuple[str, str], ...], ...]:
    branches = []
    for branch in expression.operands:
        assert isinstance(branch, AndIR)
        comparisons = []
        for item in branch.operands:
            assert isinstance(item, ComparisonIR)
            assert isinstance(item.left, ModelQuantityExpressionIR)
            comparisons.append((item.left.point.name, item.op.value))
        branches.append(tuple(comparisons))
    return tuple(branches)


def test_pair_bc_001_explicit_label_equality_lowers_to_same_decision_regions() -> None:
    lowered = _lower("target[left].label == target[right].label")
    expression = lowered.task.query.expression
    assert isinstance(expression, OrIR)
    assert _branch_signature(expression) == (
        (("left", ">"), ("right", ">")),
        (("left", "<="), ("right", "<=")),
    )
    evidence = lowered.evidence[0]
    assert isinstance(evidence, PairwiseLoweringEvidence)
    assert evidence.canonical_formula.relation == "same_binary_decision_region"
    assert evidence.compatibility_classification.value == "exact"


def test_pairwise_label_inequality_lowers_to_opposite_decision_regions() -> None:
    lowered = _lower("target[left].label != target[right].label")
    expression = lowered.task.query.expression
    assert isinstance(expression, OrIR)
    assert _branch_signature(expression) == (
        (("left", ">"), ("right", "<=")),
        (("left", "<="), ("right", ">")),
    )
    evidence = lowered.evidence[0]
    assert isinstance(evidence, PairwiseLoweringEvidence)
    assert evidence.source_intent.operator is EnumComparisonOperator.NEQ
    assert evidence.canonical_formula.relation == "different_binary_decision_region"


def test_pair_bc_002_equality_is_symmetric_and_preserves_zero_boundary() -> None:
    forward = _lower("target[left].label == target[right].label")
    reverse = _lower("target[right].label == target[left].label")
    forward_expression = forward.task.query.expression
    reverse_expression = reverse.task.query.expression
    assert isinstance(forward_expression, OrIR)
    assert isinstance(reverse_expression, OrIR)
    nf = tuple(
        tuple(sorted(branch)) for branch in _branch_signature(forward_expression)
    )
    nr = tuple(
        tuple(sorted(branch)) for branch in _branch_signature(reverse_expression)
    )
    assert nf == nr
    evidence = forward.evidence[0]
    assert isinstance(evidence, PairwiseLoweringEvidence)
    assert evidence.canonical_formula.positive_operator is EnumComparisonOperator.GT
    assert evidence.canonical_formula.negative_operator is EnumComparisonOperator.LTE
    assert evidence.boundary_policy.equality_label == "rejected"


def test_pair_bc_003_classification_equal_sugar_matches_explicit_form() -> None:
    explicit = _lower("target[left].label == target[right].label")
    sugar = _lower("CLASSIFICATION.EQUAL()")
    explicit_expression = explicit.task.query.expression
    sugar_expression = sugar.task.query.expression
    assert isinstance(explicit_expression, OrIR)
    assert isinstance(sugar_expression, OrIR)
    assert _branch_signature(explicit_expression) == _branch_signature(sugar_expression)
    evidence = sugar.evidence[0]
    assert isinstance(evidence, PairwiseLoweringEvidence)
    assert (
        evidence.transformation_id == "classification_equal_sugar_to_decision_regions"
    )


def test_problem_ir_is_removed_before_backend_normalization() -> None:
    schema = make_binary_logistic_schema()
    task = run_ir(_source("CLASSIFICATION.EQUAL()"), model_schema=schema)[0]
    assert isinstance(task.query.expression, ProblemIR)
    lowered = ModelSemanticLowerer().lower_task(task, schema=schema)
    assert not isinstance(lowered.task.query.expression, ProblemIR)


def test_pairwise_relation_rejects_the_same_model_evaluation_twice() -> None:
    with pytest.raises(
        UnsupportedObservableLoweringError,
        match="require two distinct model evaluations",
    ):
        _lower("target[left].label == target[left].label")
