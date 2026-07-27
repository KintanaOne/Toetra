from __future__ import annotations

from toetra._compatibility.enums import CompatibilityClassification
from toetra._compiler.ir.ir1.nodes import ComparisonIR
from toetra._compiler.ir.ir1.outputs import OutputObservableExpressionIR
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.schema.output_schema import ClassificationOutputSchema
from toetra._models.semantics.binary_classification_common import (
    ALL_CONCLUSIONS,
    APPROXIMATE_PROBABILITY_CONCLUSIONS,
    ORDER_OPERATORS,
    BinaryClassificationLoweringProfile,
    LogicalLoweringResult,
    boundary_policy,
    numeric_literal,
    quantity,
    reverse_comparison,
    threshold_constant,
)
from toetra._models.semantics.errors import (
    InvalidModelSemanticProfileError,
    UnsupportedObservableLoweringError,
)
from toetra._models.semantics.evidence import (
    CanonicalConstraintEvidence,
    LoweringEvidence,
    ObservableIntentEvidence,
)
from toetra._models.semantics.logistic_probability import (
    logit_threshold_interval,
    parse_probability_literal,
)


def lower_probability_comparison(
    *,
    comparison: ComparisonIR,
    observable: OutputObservableExpressionIR,
    literal: object,
    observable_on_left: bool,
    output: ClassificationOutputSchema,
    positive_polarity: bool,
    in_restriction: bool,
    profile: BinaryClassificationLoweringProfile,
) -> LogicalLoweringResult:
    if not output.probability_available:
        raise UnsupportedObservableLoweringError(
            "The selected classification output does not expose probabilities"
        )
    if observable.label is None:
        raise InvalidModelSemanticProfileError(
            "Class-probability IR is missing its selected label"
        )
    parsed_literal = numeric_literal(literal)
    if parsed_literal is None:
        raise UnsupportedObservableLoweringError(
            "Class-probability properties require a numeric literal threshold"
        )
    literal_value, literal_dtype, literal_lexeme = parsed_literal
    if isinstance(literal_value, bool) or literal_dtype not in {
        EnumDataType.INT,
        EnumDataType.FLOAT,
    }:
        raise UnsupportedObservableLoweringError(
            "Class-probability thresholds must be numeric literals"
        )
    if comparison.op not in ORDER_OPERATORS:
        raise UnsupportedObservableLoweringError(
            "Class-probability lowering initially supports only <, <=, >, and >="
        )

    try:
        probability = parse_probability_literal(
            value=literal_value,
            source_lexeme=literal_lexeme,
        )
    except ValueError as exc:
        raise UnsupportedObservableLoweringError(str(exc)) from exc

    interval = logit_threshold_interval(probability)
    if in_restriction and not interval.exact:
        raise UnsupportedObservableLoweringError(
            "Non-exact probability thresholds in scope restrictions are "
            "deferred because approximating an admissible domain requires "
            "a goal-specific policy"
        )

    normalized_op = (
        comparison.op if observable_on_left else reverse_comparison(comparison.op)
    )
    negative_label, positive_label = output.labels
    selected_label = observable.label.value
    if selected_label == positive_label:
        oriented_interval = interval
        canonical_op = normalized_op
        exact_expression = interval.expression
    elif selected_label == negative_label:
        oriented_interval = interval.negated()
        canonical_op = reverse_comparison(normalized_op)
        exact_expression = f"-{interval.expression}"
    else:
        raise InvalidModelSemanticProfileError(
            f"Label {selected_label!r} is not part of the binary output schema"
        )

    predicate_relation = "under" if positive_polarity else "over"
    selected_threshold, selected_bound = oriented_interval.selected_bound(
        operator=canonical_op,
        predicate_relation=predicate_relation,
    )
    threshold_text = format(selected_threshold, "f")
    model_quantity = quantity(profile, observable)
    threshold = threshold_constant(
        selected_threshold,
        source_lexeme=threshold_text,
    )
    canonical = ComparisonIR(
        left=model_quantity,
        op=canonical_op,
        right=threshold,
    )

    classification = (
        CompatibilityClassification.EXACT
        if interval.exact
        else CompatibilityClassification.SOUND_UNDER_APPROXIMATION
    )
    permitted = (
        ALL_CONCLUSIONS if interval.exact else APPROXIMATE_PROBABILITY_CONCLUSIONS
    )
    evidence = LoweringEvidence(
        evaluation=observable.evaluation,
        source_intent=ObservableIntentEvidence(
            observable=observable.observable,
            operator=comparison.op,
            label_value=selected_label,
            label_dtype=observable.label.dtype,
            observable_on_left=observable_on_left,
            property_threshold=format(probability, "f"),
            property_threshold_dtype=literal_dtype,
            logical_polarity=("positive" if positive_polarity else "negative"),
        ),
        semantic_profile_id=profile.profile_id,
        semantic_profile_version=profile.version,
        transformation_id=profile.probability_transformation_id,
        transformation_version=profile.probability_transformation_version,
        canonical_constraint=CanonicalConstraintEvidence(
            quantity_kind=model_quantity.quantity_kind.value,
            operator=canonical_op,
            threshold=threshold_text,
            threshold_dtype=EnumDataType.FLOAT,
            exact_threshold_expression=exact_expression,
            threshold_lower_bound=format(oriented_interval.lower, "f"),
            threshold_upper_bound=format(oriented_interval.upper, "f"),
            selected_bound=selected_bound,
            precision_digits=oriented_interval.precision_digits,
            working_precision_digits=oriented_interval.working_precision_digits,
            guard_digits=oriented_interval.guard_digits,
        ),
        boundary_policy=boundary_policy(output),
        compatibility_classification=classification,
        permitted_conclusions=permitted,
    )
    return LogicalLoweringResult(expression=canonical, evidence=(evidence,))
