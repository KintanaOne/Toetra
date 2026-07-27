from __future__ import annotations

from decimal import Decimal

from toetra._compatibility.enums import CompatibilityClassification
from toetra._compiler.ir.ir1.model_quantities import ModelQuantityExpressionIR
from toetra._compiler.ir.ir1.nodes import (
    AndIR,
    ComparisonIR,
    LogicalIR,
    ModelEvaluationIR,
    OrIR,
    ProblemIR,
)
from toetra._compiler.ir.ir1.outputs import OutputObservableExpressionIR
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._language.vocabulary.functions import EnumFunction
from toetra._language.vocabulary.operators import EnumComparisonOperator
from toetra._language.vocabulary.problems import EnumProblem
from toetra._models.schema.output_schema import (
    ClassificationOutputSchema,
    EnumOutputObservable,
)
from toetra._models.semantics.binary_classification_common import (
    ALL_CONCLUSIONS,
    BinaryClassificationLoweringProfile,
    LogicalLoweringResult,
    boundary_policy,
    quantity_from_evaluation,
    threshold_constant,
)
from toetra._models.semantics.errors import (
    InvalidModelSemanticProfileError,
    UnsupportedObservableLoweringError,
)
from toetra._models.semantics.evidence import (
    PairwiseCanonicalFormulaEvidence,
    PairwiseLoweringEvidence,
    PairwiseObservableIntentEvidence,
)


def lower_problem(
    problem: ProblemIR,
    *,
    output: ClassificationOutputSchema,
    positive_polarity: bool,
    profile: BinaryClassificationLoweringProfile,
) -> LogicalLoweringResult:
    if not (
        problem.problem is EnumProblem.CLASSIFICATION
        and problem.function is EnumFunction.EQUAL
    ):
        return LogicalLoweringResult(expression=problem)
    evaluations = () if problem.args is None else problem.args.get("evaluations", ())
    if not isinstance(evaluations, tuple) or len(evaluations) != 2:
        raise UnsupportedObservableLoweringError(
            "CLASSIFICATION.EQUAL() requires exactly two resolved model evaluations"
        )
    if not all(isinstance(item, ModelEvaluationIR) for item in evaluations):
        raise InvalidModelSemanticProfileError(
            "CLASSIFICATION.EQUAL() reached model lowering with invalid "
            "evaluation metadata"
        )
    left, right = evaluations
    return lower_pairwise_label_relation(
        left=left,
        right=right,
        operator=EnumComparisonOperator.EQ,
        output=output,
        positive_polarity=positive_polarity,
        transformation_id="classification_equal_sugar_to_decision_regions",
        profile=profile,
    )


def lower_pairwise_observable_comparison(
    *,
    comparison: ComparisonIR,
    left: OutputObservableExpressionIR,
    right: OutputObservableExpressionIR,
    output: ClassificationOutputSchema,
    positive_polarity: bool,
    profile: BinaryClassificationLoweringProfile,
) -> LogicalLoweringResult:
    if (
        left.observable is not EnumOutputObservable.PREDICTED_LABEL
        or right.observable is not EnumOutputObservable.PREDICTED_LABEL
    ):
        raise UnsupportedObservableLoweringError(
            "Pairwise classification initially supports predicted-label relations only"
        )
    if comparison.op not in {EnumComparisonOperator.EQ, EnumComparisonOperator.NEQ}:
        raise UnsupportedObservableLoweringError(
            "Pairwise predicted labels support only equality and inequality"
        )
    if left.evaluation == right.evaluation:
        raise UnsupportedObservableLoweringError(
            "Pairwise predicted-label relations require two distinct model evaluations"
        )
    return lower_pairwise_label_relation(
        left=left.evaluation,
        right=right.evaluation,
        operator=comparison.op,
        output=output,
        positive_polarity=positive_polarity,
        transformation_id="pairwise_predicted_labels_to_decision_regions",
        profile=profile,
    )


def lower_pairwise_label_relation(
    *,
    left: ModelEvaluationIR,
    right: ModelEvaluationIR,
    operator: EnumComparisonOperator,
    output: ClassificationOutputSchema,
    positive_polarity: bool,
    transformation_id: str,
    profile: BinaryClassificationLoweringProfile,
) -> LogicalLoweringResult:
    if operator not in {EnumComparisonOperator.EQ, EnumComparisonOperator.NEQ}:
        raise UnsupportedObservableLoweringError(
            "Pairwise label lowering supports only equality and inequality"
        )
    left_quantity = quantity_from_evaluation(profile, left)
    right_quantity = quantity_from_evaluation(profile, right)
    same_region = operator is EnumComparisonOperator.EQ
    canonical = pairwise_decision_region_formula(
        left_quantity,
        right_quantity,
        same_region=same_region,
    )
    relation = (
        "same_binary_decision_region"
        if same_region
        else "different_binary_decision_region"
    )
    evidence = PairwiseLoweringEvidence(
        evaluations=(left, right),
        source_intent=PairwiseObservableIntentEvidence(
            observable=EnumOutputObservable.PREDICTED_LABEL,
            operator=operator,
            related_observable=EnumOutputObservable.PREDICTED_LABEL,
            logical_polarity="positive" if positive_polarity else "negative",
        ),
        semantic_profile_id=profile.profile_id,
        semantic_profile_version=profile.version,
        transformation_id=transformation_id,
        transformation_version="1",
        canonical_formula=PairwiseCanonicalFormulaEvidence(
            quantity_kind=left_quantity.quantity_kind.value,
            relation=relation,
            positive_operator=EnumComparisonOperator.GT,
            negative_operator=EnumComparisonOperator.LTE,
            threshold="0",
            threshold_dtype=EnumDataType.FLOAT,
        ),
        boundary_policy=boundary_policy(output),
        compatibility_classification=CompatibilityClassification.EXACT,
        permitted_conclusions=ALL_CONCLUSIONS,
    )
    return LogicalLoweringResult(expression=canonical, evidence=(evidence,))


def pairwise_decision_region_formula(
    left: ModelQuantityExpressionIR,
    right: ModelQuantityExpressionIR,
    *,
    same_region: bool,
) -> LogicalIR:
    left_positive = region_comparison(left, positive=True)
    left_negative = region_comparison(left, positive=False)
    right_positive = region_comparison(right, positive=True)
    right_negative = region_comparison(right, positive=False)
    branches = (
        (
            AndIR([left_positive, right_positive]),
            AndIR([left_negative, right_negative]),
        )
        if same_region
        else (
            AndIR([left_positive, right_negative]),
            AndIR([left_negative, right_positive]),
        )
    )
    return OrIR(list(branches))


def region_comparison(
    model_quantity: ModelQuantityExpressionIR,
    *,
    positive: bool,
) -> ComparisonIR:
    return ComparisonIR(
        left=model_quantity,
        op=EnumComparisonOperator.GT if positive else EnumComparisonOperator.LTE,
        right=threshold_constant(Decimal(0), source_lexeme="0"),
    )
