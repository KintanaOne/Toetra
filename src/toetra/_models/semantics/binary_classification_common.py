from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from toetra._compatibility.enums import ConclusionKind
from toetra._compiler.ir.ir1.model_quantities import (
    EnumModelQuantityKind,
    ModelQuantityExpressionIR,
)
from toetra._compiler.ir.ir1.nodes import (
    ConstantExpressionIR,
    LogicalIR,
    ModelEvaluationIR,
    ScalarValueSource,
    UnaryArithmeticExpressionIR,
)
from toetra._compiler.ir.ir1.outputs import OutputObservableExpressionIR
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._language.vocabulary.operators import (
    EnumComparisonOperator,
    EnumUnaryOperator,
)
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.schema.output_schema import ClassificationOutputSchema
from toetra._models.semantics.errors import InvalidModelSemanticProfileError
from toetra._models.semantics.evidence import (
    BoundaryPolicyEvidence,
    SemanticLoweringEvidence,
)

ALL_CONCLUSIONS = tuple(ConclusionKind)
APPROXIMATE_PROBABILITY_CONCLUSIONS = (
    ConclusionKind.UNIVERSAL_PROOF,
    ConclusionKind.EXISTENTIAL_WITNESS,
)
ORDER_OPERATORS = frozenset(
    {
        EnumComparisonOperator.LT,
        EnumComparisonOperator.LTE,
        EnumComparisonOperator.GT,
        EnumComparisonOperator.GTE,
    }
)


@dataclass(frozen=True)
class BinaryClassificationLoweringProfile:
    profile_id: str
    version: str
    label_transformation_id: str
    probability_transformation_id: str
    label_transformation_version: str
    probability_transformation_version: str


@dataclass(frozen=True)
class LogicalLoweringResult:
    expression: LogicalIR
    evidence: tuple[SemanticLoweringEvidence, ...] = ()


def quantity(
    profile: BinaryClassificationLoweringProfile,
    observable: OutputObservableExpressionIR,
) -> ModelQuantityExpressionIR:
    return quantity_from_evaluation(profile, observable.evaluation)


def quantity_from_evaluation(
    profile: BinaryClassificationLoweringProfile,
    evaluation: ModelEvaluationIR,
) -> ModelQuantityExpressionIR:
    return ModelQuantityExpressionIR(
        evaluation=evaluation,
        quantity_kind=EnumModelQuantityKind.ORIENTED_DECISION_VALUE,
        semantic_profile_id=profile.profile_id,
    )


def threshold_constant(
    value: Decimal,
    *,
    source_lexeme: str,
) -> ConstantExpressionIR:
    return ConstantExpressionIR(
        value=value,
        dtype=EnumDataType.FLOAT,
        source_kind=ScalarValueSource.LITERAL,
        source_lexeme=source_lexeme,
    )


def numeric_literal(
    expression: object,
) -> tuple[object, EnumDataType, str | None] | None:
    if isinstance(expression, ConstantExpressionIR):
        return expression.value, expression.dtype, expression.source_lexeme
    if not isinstance(expression, UnaryArithmeticExpressionIR):
        return None
    operand = expression.operand
    if not isinstance(operand, ConstantExpressionIR):
        return None
    if isinstance(operand.value, bool) or not isinstance(
        operand.value,
        (int, float),
    ):
        return None
    if expression.operator is EnumUnaryOperator.PLUS:
        value = +operand.value
        prefix = "+"
    elif expression.operator is EnumUnaryOperator.MINUS:
        value = -operand.value
        prefix = "-"
    else:
        return None
    source = (
        f"{prefix}{operand.source_lexeme}"
        if operand.source_lexeme is not None
        else str(value)
    )
    return value, operand.dtype, source


def canonical_label_operator(
    *,
    source_op: EnumComparisonOperator,
    is_positive_label: bool,
) -> EnumComparisonOperator:
    equality = source_op is EnumComparisonOperator.EQ
    predicts_positive = equality if is_positive_label else not equality
    return (
        EnumComparisonOperator.GT if predicts_positive else EnumComparisonOperator.LTE
    )


def reverse_comparison(
    operator: EnumComparisonOperator,
) -> EnumComparisonOperator:
    mapping = {
        EnumComparisonOperator.LT: EnumComparisonOperator.GT,
        EnumComparisonOperator.LTE: EnumComparisonOperator.GTE,
        EnumComparisonOperator.GT: EnumComparisonOperator.LT,
        EnumComparisonOperator.GTE: EnumComparisonOperator.LTE,
        EnumComparisonOperator.EQ: EnumComparisonOperator.EQ,
        EnumComparisonOperator.NEQ: EnumComparisonOperator.NEQ,
    }
    return mapping[operator]


def boundary_policy(
    output: ClassificationOutputSchema,
) -> BoundaryPolicyEvidence:
    negative_label, _positive_label = output.labels
    return BoundaryPolicyEvidence(
        positive_operator=EnumComparisonOperator.GT,
        positive_threshold="0",
        equality_label=negative_label,
    )


def validated_output(schema: ModelSchema) -> ClassificationOutputSchema:
    output = schema.output_schema
    if not isinstance(output, ClassificationOutputSchema):
        raise InvalidModelSemanticProfileError(
            "Binary classification lowering requires a classification output"
        )
    if len(output.labels) != 2:
        raise InvalidModelSemanticProfileError(
            "Binary classification lowering requires exactly two ordered labels"
        )
    return output
