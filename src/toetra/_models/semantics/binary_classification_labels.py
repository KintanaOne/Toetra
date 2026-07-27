from __future__ import annotations

from decimal import Decimal

from toetra._compatibility.enums import CompatibilityClassification
from toetra._compiler.ir.ir1.nodes import ComparisonIR, ConstantExpressionIR
from toetra._compiler.ir.ir1.outputs import OutputObservableExpressionIR
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._language.vocabulary.operators import EnumComparisonOperator
from toetra._models.schema.output_schema import ClassificationOutputSchema
from toetra._models.semantics.binary_classification_common import (
    ALL_CONCLUSIONS,
    BinaryClassificationLoweringProfile,
    LogicalLoweringResult,
    boundary_policy,
    canonical_label_operator,
    quantity,
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


def lower_label_comparison(
    *,
    comparison: ComparisonIR,
    observable: OutputObservableExpressionIR,
    literal: object,
    observable_on_left: bool,
    output: ClassificationOutputSchema,
    positive_polarity: bool,
    profile: BinaryClassificationLoweringProfile,
) -> LogicalLoweringResult:
    if not isinstance(literal, ConstantExpressionIR):
        raise UnsupportedObservableLoweringError(
            "Predicted-label properties initially require a literal label"
        )
    if comparison.op not in {
        EnumComparisonOperator.EQ,
        EnumComparisonOperator.NEQ,
    }:
        raise UnsupportedObservableLoweringError(
            "Predicted-label lowering supports only equality and inequality"
        )

    label = literal.value
    negative_label, positive_label = output.labels
    if label == positive_label:
        is_positive = True
    elif label == negative_label:
        is_positive = False
    else:
        raise InvalidModelSemanticProfileError(
            f"Label {label!r} is not part of the binary output schema"
        )

    canonical_op = canonical_label_operator(
        source_op=comparison.op,
        is_positive_label=is_positive,
    )
    model_quantity = quantity(profile, observable)
    threshold = threshold_constant(Decimal(0), source_lexeme="0")
    canonical = ComparisonIR(
        left=model_quantity,
        op=canonical_op,
        right=threshold,
    )
    evidence = LoweringEvidence(
        evaluation=observable.evaluation,
        source_intent=ObservableIntentEvidence(
            observable=observable.observable,
            operator=comparison.op,
            label_value=label,
            label_dtype=literal.dtype,
            observable_on_left=observable_on_left,
            logical_polarity=("positive" if positive_polarity else "negative"),
        ),
        semantic_profile_id=profile.profile_id,
        semantic_profile_version=profile.version,
        transformation_id=profile.label_transformation_id,
        transformation_version=profile.label_transformation_version,
        canonical_constraint=CanonicalConstraintEvidence(
            quantity_kind=model_quantity.quantity_kind.value,
            operator=canonical_op,
            threshold="0",
            threshold_dtype=EnumDataType.FLOAT,
        ),
        boundary_policy=boundary_policy(output),
        compatibility_classification=CompatibilityClassification.EXACT,
        permitted_conclusions=ALL_CONCLUSIONS,
    )
    return LogicalLoweringResult(expression=canonical, evidence=(evidence,))
