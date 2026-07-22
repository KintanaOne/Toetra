from __future__ import annotations

from decimal import Decimal

import pytest

from dsl.compatibility.enums import CompatibilityClassification, ConclusionKind
from dsl.ir.ir1.model_quantities import ModelQuantityExpressionIR
from dsl.ir.ir1.nodes import ComparisonIR, ConstantExpressionIR, NotIR
from dsl.ir.ir1.run_ir1 import run_ir
from dsl.language.vocabulary.operators import EnumComparisonOperator
from model.semantics.errors import UnsupportedObservableLoweringError
from model.semantics.evidence import LoweringEvidence
from model.semantics.lowering import ModelSemanticLowerer
from test.fixtures.model_semantic_lowering import make_binary_logistic_schema


def _property(
    expression: str,
    *,
    quantifier: str = "forall",
    restriction: str | None = None,
) -> str:
    where = f" where {restriction}" if restriction is not None else ""
    return f"""\
model := "credit.joblib"
target := decision

[LOGIC]:
{quantifier} applicant{where} =>
    {expression}
"""


def _lower(expression: str):
    schema = make_binary_logistic_schema()
    task = run_ir(_property(expression), model_schema=schema)[0]
    return ModelSemanticLowerer().lower_task(task, schema=schema)


def test_positive_probability_uses_upper_logit_bound_for_positive_polarity() -> None:
    lowered = _lower('target[applicant].probability("approved") >= 0.8')

    comparison = lowered.task.query.expression
    assert isinstance(comparison, ComparisonIR)
    assert isinstance(comparison.left, ModelQuantityExpressionIR)
    assert comparison.op is EnumComparisonOperator.GTE
    assert isinstance(comparison.right, ConstantExpressionIR)
    assert isinstance(comparison.right.value, Decimal)

    evidence = lowered.evidence[0]
    assert isinstance(evidence, LoweringEvidence)
    canonical = evidence.canonical_constraint
    assert evidence.transformation_version == "2"
    assert canonical.selected_bound == "upper"
    assert canonical.threshold == canonical.threshold_upper_bound
    assert canonical.exact_threshold_expression == "logit(0.8)"
    assert canonical.precision_digits == 50
    assert canonical.working_precision_digits == 70
    assert canonical.guard_digits == 20
    payload = evidence.to_dict()["canonical_constraint"]
    assert payload["precision_digits"] == 50
    assert payload["working_precision_digits"] == 70
    assert payload["guard_digits"] == 20
    assert (
        evidence.compatibility_classification
        is CompatibilityClassification.SOUND_UNDER_APPROXIMATION
    )
    assert evidence.permitted_conclusions == (
        ConclusionKind.UNIVERSAL_PROOF,
        ConclusionKind.EXISTENTIAL_WITNESS,
    )


def test_negative_label_probability_reverses_orientation() -> None:
    lowered = _lower('target[applicant].probability("rejected") >= 0.8')

    comparison = lowered.task.query.expression
    assert isinstance(comparison, ComparisonIR)
    assert comparison.op is EnumComparisonOperator.LTE
    evidence = lowered.evidence[0]
    assert isinstance(evidence, LoweringEvidence)
    assert evidence.canonical_constraint.selected_bound == "lower"
    assert evidence.canonical_constraint.exact_threshold_expression == "-logit(0.8)"
    assert evidence.canonical_constraint.threshold.startswith("-1.386294")


def test_probability_observable_on_right_is_normalized() -> None:
    lowered = _lower('0.8 <= target[applicant].probability("approved")')

    comparison = lowered.task.query.expression
    assert isinstance(comparison, ComparisonIR)
    assert comparison.op is EnumComparisonOperator.GTE
    evidence = lowered.evidence[0]
    assert isinstance(evidence, LoweringEvidence)
    assert evidence.source_intent.observable_on_left is False


def test_native_probability_threshold_is_exact() -> None:
    lowered = _lower('target[applicant].probability("approved") > 0.5')

    comparison = lowered.task.query.expression
    assert isinstance(comparison, ComparisonIR)
    assert comparison.op is EnumComparisonOperator.GT
    assert isinstance(comparison.right, ConstantExpressionIR)
    assert comparison.right.value == Decimal(0)

    evidence = lowered.evidence[0]
    assert isinstance(evidence, LoweringEvidence)
    assert evidence.compatibility_classification is CompatibilityClassification.EXACT
    assert evidence.permitted_conclusions == tuple(ConclusionKind)
    assert evidence.canonical_constraint.selected_bound == "exact"
    assert evidence.canonical_constraint.threshold_lower_bound == "0"
    assert evidence.canonical_constraint.threshold_upper_bound == "0"


def test_negative_logical_polarity_selects_atomic_over_approximation() -> None:
    lowered = _lower('not (target[applicant].probability("approved") >= 0.8)')

    expression = lowered.task.query.expression
    assert isinstance(expression, NotIR)
    comparison = expression.operand
    assert isinstance(comparison, ComparisonIR)
    evidence = lowered.evidence[0]
    assert isinstance(evidence, LoweringEvidence)
    assert evidence.source_intent.logical_polarity == "negative"
    assert evidence.canonical_constraint.selected_bound == "lower"


def test_non_exact_probability_threshold_in_restriction_is_deferred() -> None:
    schema = make_binary_logistic_schema()
    task = run_ir(
        _property(
            'target[applicant].label == "approved"',
            restriction='target[applicant].probability("approved") >= 0.8',
        ),
        model_schema=schema,
    )[0]

    with pytest.raises(
        UnsupportedObservableLoweringError,
        match="scope restrictions",
    ):
        ModelSemanticLowerer().lower_task(task, schema=schema)


@pytest.mark.parametrize("threshold", ["0", "1", "-0.1", "1.1"])
def test_probability_threshold_must_be_strictly_inside_unit_interval(
    threshold: str,
) -> None:
    schema = make_binary_logistic_schema()
    task = run_ir(
        _property(f'target[applicant].probability("approved") >= {threshold}'),
        model_schema=schema,
    )[0]

    with pytest.raises(
        UnsupportedObservableLoweringError,
        match="strictly between 0 and 1",
    ):
        ModelSemanticLowerer().lower_task(task, schema=schema)


@pytest.mark.parametrize("operator", ["==", "!="])
def test_probability_equality_is_explicitly_deferred(operator: str) -> None:
    schema = make_binary_logistic_schema()
    task = run_ir(
        _property(f'target[applicant].probability("approved") {operator} 0.8'),
        model_schema=schema,
    )[0]

    with pytest.raises(
        UnsupportedObservableLoweringError,
        match="only <, <=, >, and >=",
    ):
        ModelSemanticLowerer().lower_task(task, schema=schema)
