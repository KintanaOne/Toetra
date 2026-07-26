from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction
from typing import Any, Mapping

from toetra._language.vocabulary.operators import EnumComparisonOperator
from toetra._reporting.values import exact_report_value, python_report_value
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.schema.output_schema import (
    ClassificationOutputSchema,
    ModelLabel,
)
from toetra._models.semantics.evidence import (
    LoweringEvidence,
    SemanticLoweringEvidence,
)

RECONSTRUCTED_PROBABILITY_PRECISION_DIGITS = 50
EvaluationKey = tuple[str, str, str]
QuantityKey = tuple[str, str, str, str]


@dataclass(frozen=True)
class ReportClassProbability:
    label: ModelLabel
    value: Decimal | None
    source: str = "reconstructed_from_oriented_decision_value"
    precision_digits: int = RECONSTRUCTED_PROBABILITY_PRECISION_DIGITS

    @property
    def python_value(self) -> float | None:
        return float(self.value) if self.value is not None else None


@dataclass(frozen=True)
class ReportModelQuantity:
    kind: str
    semantic_profile_id: str
    value: Any | None

    @property
    def python_value(self) -> Any:
        return python_report_value(self.value)


@dataclass(frozen=True)
class ReportLoweringTrace:
    observable: str
    operator: str
    label: ModelLabel | None
    property_threshold: str | None
    property_value: Any | None
    property_satisfied: bool | None
    property_margin: Decimal | None
    logical_polarity: str
    semantic_profile_id: str
    semantic_profile_version: str
    transformation_id: str
    transformation_version: str
    quantity_kind: str
    quantity_value: Any | None
    canonical_operator: str
    canonical_threshold: str
    canonical_margin: Decimal | None
    exact_threshold_expression: str | None
    threshold_lower_bound: str | None
    threshold_upper_bound: str | None
    selected_bound: str
    precision_digits: int | None
    working_precision_digits: int | None
    guard_digits: int | None
    compatibility_classification: str
    permitted_conclusions: tuple[str, ...]
    related_point_name: str | None = None
    related_property_value: Any | None = None
    related_quantity_value: Any | None = None
    canonical_formula_kind: str | None = None


@dataclass(frozen=True)
class ReportModelEvaluation:
    model_identity: str
    point_name: str
    binding_kind: str
    output_name: str
    predicted_label: ModelLabel | None
    probabilities: tuple[ReportClassProbability, ...]
    quantities: tuple[ReportModelQuantity, ...]
    native_probability_threshold: str | None
    native_decision_threshold: str | None
    equality_label: ModelLabel | None
    lowerings: tuple[ReportLoweringTrace, ...]

    @property
    def probability_values(self) -> dict[ModelLabel, float | None]:
        return {item.label: item.python_value for item in self.probabilities}

    @property
    def quantity_values(self) -> dict[str, Any]:
        return {item.kind: item.python_value for item in self.quantities}


def build_report_model_evaluations(
    *,
    schema: ModelSchema | None,
    lowering_evidence: tuple[SemanticLoweringEvidence, ...],
    quantity_values: Mapping[QuantityKey, Any],
) -> tuple[ReportModelEvaluation, ...]:
    grouped: dict[EvaluationKey, list[SemanticLoweringEvidence]] = {}
    for evidence in lowering_evidence:
        evaluations = (
            (evidence.evaluation,)
            if isinstance(evidence, LoweringEvidence)
            else evidence.evaluations
        )
        for evaluation in evaluations:
            grouped.setdefault(_evaluation_key(evaluation), []).append(evidence)
    results = []
    for key, evidences in grouped.items():
        model_identity, point_name, output_name = key
        evaluation = _evidence_evaluation_for_key(evidences[0], key)
        classification = _classification_schema(schema, output_name)
        quantity_kinds = tuple(
            dict.fromkeys(_evidence_quantity_kind(e) for e in evidences)
        )
        quantities = tuple(
            ReportModelQuantity(
                kind=k,
                semantic_profile_id=evidences[0].semantic_profile_id,
                value=quantity_values.get((model_identity, point_name, output_name, k)),
            )
            for k in quantity_kinds
        )
        quantity_by_kind = {q.kind: q.value for q in quantities}
        policy = classification.decision_policy if classification is not None else None
        predicted_label, probabilities = _public_views(
            policy=policy,
            decision_value=quantity_by_kind.get("oriented_decision_value"),
        )
        probability_map = {item.label: item.value for item in probabilities}
        traces = []
        for evidence in evidences:
            if isinstance(evidence, LoweringEvidence):
                traces.append(
                    _build_trace(
                        evidence=evidence,
                        quantity_value=quantity_by_kind.get(
                            evidence.canonical_constraint.quantity_kind
                        ),
                        predicted_label=predicted_label,
                        probability_map=probability_map,
                    )
                )
            else:
                traces.append(
                    _build_pairwise_trace(
                        evidence=evidence,
                        current_key=key,
                        policy=policy,
                        quantity_values=quantity_values,
                    )
                )
        results.append(
            ReportModelEvaluation(
                model_identity=model_identity,
                point_name=point_name,
                binding_kind=evaluation.point.binding_kind,
                output_name=output_name,
                predicted_label=predicted_label,
                probabilities=probabilities,
                quantities=quantities,
                native_probability_threshold=(
                    policy.probability_threshold if policy else None
                ),
                native_decision_threshold=(
                    policy.oriented_decision_threshold if policy else None
                ),
                equality_label=policy.equality_label if policy else None,
                lowerings=tuple(traces),
            )
        )
    return tuple(results)


def _classification_schema(schema, output_name):
    if (
        schema is not None
        and schema.output_name == output_name
        and isinstance(schema.output_schema, ClassificationOutputSchema)
    ):
        return schema.output_schema
    return None


def _public_views(*, policy, decision_value):
    if policy is None or decision_value is None:
        return None, ()
    decision_decimal = _as_decimal(decision_value)
    predicted = _label_from_quantity(policy, decision_decimal)
    positive = _sigmoid(decision_decimal)
    return predicted, (
        ReportClassProbability(
            label=policy.negative_label, value=Decimal(1) - positive
        ),
        ReportClassProbability(label=policy.positive_label, value=positive),
    )


def _build_trace(*, evidence, quantity_value, predicted_label, probability_map):
    intent = evidence.source_intent
    canonical = evidence.canonical_constraint
    property_value = None
    satisfied = None
    property_margin = None
    if intent.observable.value == "predicted_label":
        property_value = predicted_label
        if predicted_label is not None:
            satisfied = _compare(predicted_label, intent.operator, intent.label_value)
    elif intent.observable.value == "class_probability":
        property_value = probability_map.get(intent.label_value)
        if property_value is not None and intent.property_threshold is not None:
            threshold = Decimal(intent.property_threshold)
            satisfied = _compare(property_value, intent.operator, threshold)
            property_margin = _margin(
                _as_decimal(property_value), intent.operator, threshold
            )
    canonical_margin = (
        _margin(
            _as_decimal(quantity_value),
            canonical.operator,
            Decimal(canonical.threshold),
        )
        if quantity_value is not None
        else None
    )
    return ReportLoweringTrace(
        observable=intent.observable.value,
        operator=intent.operator.value,
        label=intent.label_value,
        property_threshold=intent.property_threshold,
        property_value=property_value,
        property_satisfied=satisfied,
        property_margin=property_margin,
        logical_polarity=intent.logical_polarity,
        semantic_profile_id=evidence.semantic_profile_id,
        semantic_profile_version=evidence.semantic_profile_version,
        transformation_id=evidence.transformation_id,
        transformation_version=evidence.transformation_version,
        quantity_kind=canonical.quantity_kind,
        quantity_value=quantity_value,
        canonical_operator=canonical.operator.value,
        canonical_threshold=canonical.threshold,
        canonical_margin=canonical_margin,
        exact_threshold_expression=canonical.exact_threshold_expression,
        threshold_lower_bound=canonical.threshold_lower_bound,
        threshold_upper_bound=canonical.threshold_upper_bound,
        selected_bound=canonical.selected_bound,
        precision_digits=canonical.precision_digits,
        working_precision_digits=canonical.working_precision_digits,
        guard_digits=canonical.guard_digits,
        compatibility_classification=evidence.compatibility_classification.value,
        permitted_conclusions=tuple(c.value for c in evidence.permitted_conclusions),
    )


def _build_pairwise_trace(*, evidence, current_key, policy, quantity_values):
    current = _evidence_evaluation_for_key(evidence, current_key)
    related = (
        evidence.evaluations[1]
        if current == evidence.evaluations[0]
        else evidence.evaluations[0]
    )
    kind = evidence.canonical_formula.quantity_kind
    current_quantity = quantity_values.get((*current_key, kind))
    related_key = _evaluation_key(related)
    related_quantity = quantity_values.get((*related_key, kind))
    current_label = (
        _label_from_quantity(policy, _as_decimal(current_quantity))
        if policy and current_quantity is not None
        else None
    )
    related_label = (
        _label_from_quantity(policy, _as_decimal(related_quantity))
        if policy and related_quantity is not None
        else None
    )
    satisfied = (
        _compare(current_label, evidence.source_intent.operator, related_label)
        if current_label is not None and related_label is not None
        else None
    )
    return ReportLoweringTrace(
        observable=evidence.source_intent.observable.value,
        operator=evidence.source_intent.operator.value,
        label=None,
        property_threshold=None,
        property_value=current_label,
        property_satisfied=satisfied,
        property_margin=None,
        logical_polarity=evidence.source_intent.logical_polarity,
        semantic_profile_id=evidence.semantic_profile_id,
        semantic_profile_version=evidence.semantic_profile_version,
        transformation_id=evidence.transformation_id,
        transformation_version=evidence.transformation_version,
        quantity_kind=kind,
        quantity_value=current_quantity,
        canonical_operator=evidence.source_intent.operator.value,
        canonical_threshold=evidence.canonical_formula.threshold,
        canonical_margin=None,
        exact_threshold_expression=None,
        threshold_lower_bound=None,
        threshold_upper_bound=None,
        selected_bound="exact",
        precision_digits=None,
        working_precision_digits=None,
        guard_digits=None,
        compatibility_classification=evidence.compatibility_classification.value,
        permitted_conclusions=tuple(c.value for c in evidence.permitted_conclusions),
        related_point_name=related.point.name,
        related_property_value=related_label,
        related_quantity_value=related_quantity,
        canonical_formula_kind=evidence.canonical_formula.relation,
    )


def _evaluation_key(evaluation):
    return (evaluation.model_identity, evaluation.point.name, evaluation.output_name)


def _evidence_evaluation_for_key(evidence, key):
    if isinstance(evidence, LoweringEvidence):
        if _evaluation_key(evidence.evaluation) != key:
            raise ValueError("Lowering evidence does not match report evaluation key")
        return evidence.evaluation
    for evaluation in evidence.evaluations:
        if _evaluation_key(evaluation) == key:
            return evaluation
    raise ValueError("Pairwise lowering evidence does not match report evaluation key")


def _evidence_quantity_kind(evidence):
    return (
        evidence.canonical_constraint.quantity_kind
        if isinstance(evidence, LoweringEvidence)
        else evidence.canonical_formula.quantity_kind
    )


def _label_from_quantity(policy, quantity):
    return (
        policy.positive_label
        if quantity > Decimal(policy.oriented_decision_threshold)
        else policy.negative_label
    )


def _sigmoid(value):
    with localcontext() as context:
        context.prec = RECONSTRUCTED_PROBABILITY_PRECISION_DIGITS
        if value >= 0:
            exp_neg = (-value).exp(context=context)
            return Decimal(1) / (Decimal(1) + exp_neg)
        exp_pos = value.exp(context=context)
        return exp_pos / (Decimal(1) + exp_pos)


def _as_decimal(value):
    exact = exact_report_value(value)
    if isinstance(exact, Decimal):
        return exact
    if isinstance(exact, Fraction):
        with localcontext() as context:
            context.prec = 80
            return Decimal(exact.numerator) / Decimal(exact.denominator)
    if isinstance(exact, bool):
        return Decimal(int(exact))
    if isinstance(exact, int):
        return Decimal(exact)
    if isinstance(exact, float):
        return Decimal(str(exact))
    if isinstance(exact, str):
        return Decimal(exact)
    raise TypeError(f"Cannot convert {type(exact).__name__} to Decimal")


def _compare(left, operator, right):
    return {
        EnumComparisonOperator.EQ: left == right,
        EnumComparisonOperator.NEQ: left != right,
        EnumComparisonOperator.LT: left < right,
        EnumComparisonOperator.LTE: left <= right,
        EnumComparisonOperator.GT: left > right,
        EnumComparisonOperator.GTE: left >= right,
    }[operator]


def _margin(value, operator, threshold):
    if operator in {EnumComparisonOperator.GT, EnumComparisonOperator.GTE}:
        return value - threshold
    if operator in {EnumComparisonOperator.LT, EnumComparisonOperator.LTE}:
        return threshold - value
    return None
