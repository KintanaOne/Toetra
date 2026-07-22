from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal

from dsl.compatibility.enums import CompatibilityClassification, ConclusionKind
from dsl.ir.ir1.model_quantities import (
    EnumModelQuantityKind,
    ModelQuantityExpressionIR,
)
from dsl.ir.ir1.nodes import (
    AndIR,
    ComparisonIR,
    ConstantExpressionIR,
    ImplyIR,
    LogicalIR,
    NotIR,
    OrIR,
    ProblemIR,
    QueryIR,
    RestrictionIR,
    ScalarValueSource,
    ModelEvaluationIR,
    UnaryArithmeticExpressionIR,
    VerificationTask,
)
from dsl.ir.ir1.scalar import iter_scalar_expressions
from dsl.ir.ir1.outputs import OutputObservableExpressionIR
from dsl.language.vocabulary.functions import EnumFunction
from dsl.language.vocabulary.operators import (
    EnumComparisonOperator,
    EnumUnaryOperator,
)
from dsl.language.vocabulary.problems import EnumProblem
from dsl.semantic.types.enums import EnumDataType
from model.families import (
    BINARY_LOGISTIC_AFFINE_MODEL_FAMILY,
    BINARY_LOGISTIC_AFFINE_SEMANTIC_PROFILE_ID,
)
from model.schema.model_schema import ModelSchema
from model.schema.output_schema import (
    ClassificationOutputSchema,
    EnumOutputObservable,
)
from model.semantics.base import LoweredVerificationTask
from model.semantics.errors import (
    InvalidModelSemanticProfileError,
    UnsupportedObservableLoweringError,
)
from model.semantics.evidence import (
    BoundaryPolicyEvidence,
    CanonicalConstraintEvidence,
    LoweringEvidence,
    ObservableIntentEvidence,
    PairwiseCanonicalFormulaEvidence,
    PairwiseLoweringEvidence,
    PairwiseObservableIntentEvidence,
    SemanticLoweringEvidence,
)
from model.semantics.logistic_probability import (
    logit_threshold_interval,
    parse_probability_literal,
)

__all__ = [
    "BINARY_LOGISTIC_AFFINE_MODEL_FAMILY",
    "BinaryLogisticAffineClassificationProfile",
]

_ALL_CONCLUSIONS = tuple(ConclusionKind)
_APPROXIMATE_PROBABILITY_CONCLUSIONS = (
    ConclusionKind.UNIVERSAL_PROOF,
    ConclusionKind.EXISTENTIAL_WITNESS,
)
_ORDER_OPERATORS = frozenset(
    {
        EnumComparisonOperator.LT,
        EnumComparisonOperator.LTE,
        EnumComparisonOperator.GT,
        EnumComparisonOperator.GTE,
    }
)


@dataclass(frozen=True)
class _LogicalResult:
    expression: LogicalIR
    evidence: tuple[SemanticLoweringEvidence, ...] = ()


class BinaryLogisticAffineClassificationProfile:
    """Initial binary classification semantics independent from implementation."""

    profile_id = BINARY_LOGISTIC_AFFINE_SEMANTIC_PROFILE_ID
    version = "1"
    label_transformation_id = "predicted_label_literal_to_oriented_decision_value"
    probability_transformation_id = (
        "class_probability_threshold_to_oriented_decision_value"
    )
    label_transformation_version = "1"
    probability_transformation_version = "2"

    def lower_task(
        self,
        task: VerificationTask,
        *,
        schema: ModelSchema,
    ) -> LoweredVerificationTask:
        output = self._validated_output(schema)
        query_result = self._lower_logical(
            task.query.expression,
            output=output,
            positive_polarity=True,
            in_restriction=False,
        )

        scope = task.scope
        restriction_evidence: tuple[SemanticLoweringEvidence, ...] = ()
        if scope.restriction is not None:
            restriction_result = self._lower_logical(
                scope.restriction.expression,
                output=output,
                positive_polarity=True,
                in_restriction=True,
            )
            scope = replace(
                scope,
                restriction=RestrictionIR(
                    expression=restriction_result.expression,
                    provenance=scope.restriction.provenance,
                ),
            )
            restriction_evidence = restriction_result.evidence

        return LoweredVerificationTask(
            task=replace(
                task,
                scope=scope,
                query=QueryIR(expression=query_result.expression),
            ),
            evidence=restriction_evidence + query_result.evidence,
        )

    def _lower_logical(
        self,
        node: LogicalIR,
        *,
        output: ClassificationOutputSchema,
        positive_polarity: bool,
        in_restriction: bool,
    ) -> _LogicalResult:
        if isinstance(node, ComparisonIR):
            return self._lower_comparison(
                node,
                output=output,
                positive_polarity=positive_polarity,
                in_restriction=in_restriction,
            )

        if isinstance(node, ProblemIR):
            return self._lower_problem(
                node, output=output, positive_polarity=positive_polarity
            )

        if isinstance(node, AndIR):
            results = tuple(
                self._lower_logical(
                    operand,
                    output=output,
                    positive_polarity=positive_polarity,
                    in_restriction=in_restriction,
                )
                for operand in node.operands
            )
            return _LogicalResult(
                expression=AndIR([result.expression for result in results]),
                evidence=tuple(item for result in results for item in result.evidence),
            )

        if isinstance(node, OrIR):
            results = tuple(
                self._lower_logical(
                    operand,
                    output=output,
                    positive_polarity=positive_polarity,
                    in_restriction=in_restriction,
                )
                for operand in node.operands
            )
            return _LogicalResult(
                expression=OrIR([result.expression for result in results]),
                evidence=tuple(item for result in results for item in result.evidence),
            )

        if isinstance(node, NotIR):
            result = self._lower_logical(
                node.operand,
                output=output,
                positive_polarity=not positive_polarity,
                in_restriction=in_restriction,
            )
            return _LogicalResult(
                expression=NotIR(result.expression),
                evidence=result.evidence,
            )

        if isinstance(node, ImplyIR):
            left = self._lower_logical(
                node.left,
                output=output,
                positive_polarity=not positive_polarity,
                in_restriction=in_restriction,
            )
            right = self._lower_logical(
                node.right,
                output=output,
                positive_polarity=positive_polarity,
                in_restriction=in_restriction,
            )
            return _LogicalResult(
                expression=ImplyIR(left=left.expression, right=right.expression),
                evidence=left.evidence + right.evidence,
            )

        return _LogicalResult(expression=node)

    def _lower_comparison(
        self,
        comparison: ComparisonIR,
        *,
        output: ClassificationOutputSchema,
        positive_polarity: bool,
        in_restriction: bool,
    ) -> _LogicalResult:
        left_observable = isinstance(comparison.left, OutputObservableExpressionIR)
        right_observable = isinstance(comparison.right, OutputObservableExpressionIR)

        if not left_observable and not right_observable:
            if any(
                isinstance(item, OutputObservableExpressionIR)
                for root in (comparison.left, comparison.right)
                for item in iter_scalar_expressions(root)
            ):
                raise UnsupportedObservableLoweringError(
                    "Output observables must appear directly in the comparison; "
                    "arithmetic over probabilities is deferred"
                )
            return _LogicalResult(expression=comparison)

        if left_observable and right_observable:
            assert isinstance(comparison.left, OutputObservableExpressionIR)
            assert isinstance(comparison.right, OutputObservableExpressionIR)
            return self._lower_pairwise_observable_comparison(
                comparison=comparison,
                left=comparison.left,
                right=comparison.right,
                output=output,
                positive_polarity=positive_polarity,
            )

        observable = comparison.left if left_observable else comparison.right
        literal = comparison.right if left_observable else comparison.left
        assert isinstance(observable, OutputObservableExpressionIR)

        if observable.observable is EnumOutputObservable.CLASS_PROBABILITY:
            return self._lower_probability_comparison(
                comparison=comparison,
                observable=observable,
                literal=literal,
                observable_on_left=left_observable,
                output=output,
                positive_polarity=positive_polarity,
                in_restriction=in_restriction,
            )
        if observable.observable is EnumOutputObservable.PREDICTED_LABEL:
            return self._lower_label_comparison(
                comparison=comparison,
                observable=observable,
                literal=literal,
                observable_on_left=left_observable,
                output=output,
                positive_polarity=positive_polarity,
            )
        raise UnsupportedObservableLoweringError(
            f"Unsupported output observable {observable.observable.value!r}"
        )

    def _lower_problem(
        self,
        problem: ProblemIR,
        *,
        output: ClassificationOutputSchema,
        positive_polarity: bool,
    ) -> _LogicalResult:
        if not (
            problem.problem is EnumProblem.CLASSIFICATION
            and problem.function is EnumFunction.EQUAL
        ):
            return _LogicalResult(expression=problem)
        evaluations = (
            () if problem.args is None else problem.args.get("evaluations", ())
        )
        if not isinstance(evaluations, tuple) or len(evaluations) != 2:
            raise UnsupportedObservableLoweringError(
                "CLASSIFICATION.EQUAL() requires exactly two resolved model evaluations"
            )
        if not all(isinstance(item, ModelEvaluationIR) for item in evaluations):
            raise InvalidModelSemanticProfileError(
                "CLASSIFICATION.EQUAL() reached model lowering with invalid evaluation metadata"
            )
        left, right = evaluations
        return self._lower_pairwise_label_relation(
            left=left,
            right=right,
            operator=EnumComparisonOperator.EQ,
            output=output,
            positive_polarity=positive_polarity,
            transformation_id="classification_equal_sugar_to_decision_regions",
        )

    def _lower_pairwise_observable_comparison(
        self,
        *,
        comparison: ComparisonIR,
        left: OutputObservableExpressionIR,
        right: OutputObservableExpressionIR,
        output: ClassificationOutputSchema,
        positive_polarity: bool,
    ) -> _LogicalResult:
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
        return self._lower_pairwise_label_relation(
            left=left.evaluation,
            right=right.evaluation,
            operator=comparison.op,
            output=output,
            positive_polarity=positive_polarity,
            transformation_id="pairwise_predicted_labels_to_decision_regions",
        )

    def _lower_pairwise_label_relation(
        self,
        *,
        left: ModelEvaluationIR,
        right: ModelEvaluationIR,
        operator: EnumComparisonOperator,
        output: ClassificationOutputSchema,
        positive_polarity: bool,
        transformation_id: str,
    ) -> _LogicalResult:
        if operator not in {EnumComparisonOperator.EQ, EnumComparisonOperator.NEQ}:
            raise UnsupportedObservableLoweringError(
                "Pairwise label lowering supports only equality and inequality"
            )
        left_quantity = self._quantity_from_evaluation(left)
        right_quantity = self._quantity_from_evaluation(right)
        same_region = operator is EnumComparisonOperator.EQ
        canonical = self._pairwise_decision_region_formula(
            left_quantity, right_quantity, same_region=same_region
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
            semantic_profile_id=self.profile_id,
            semantic_profile_version=self.version,
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
            boundary_policy=self._boundary_policy(output),
            compatibility_classification=CompatibilityClassification.EXACT,
            permitted_conclusions=_ALL_CONCLUSIONS,
        )
        return _LogicalResult(expression=canonical, evidence=(evidence,))

    def _pairwise_decision_region_formula(
        self,
        left: ModelQuantityExpressionIR,
        right: ModelQuantityExpressionIR,
        *,
        same_region: bool,
    ) -> LogicalIR:
        lp, ln = self._region_comparison(left, positive=True), self._region_comparison(
            left, positive=False
        )
        rp, rn = self._region_comparison(right, positive=True), self._region_comparison(
            right, positive=False
        )
        branches = (
            (AndIR([lp, rp]), AndIR([ln, rn]))
            if same_region
            else (AndIR([lp, rn]), AndIR([ln, rp]))
        )
        return OrIR(list(branches))

    def _region_comparison(
        self, quantity: ModelQuantityExpressionIR, *, positive: bool
    ) -> ComparisonIR:
        return ComparisonIR(
            left=quantity,
            op=EnumComparisonOperator.GT if positive else EnumComparisonOperator.LTE,
            right=self._threshold_constant(Decimal(0), source_lexeme="0"),
        )

    def _lower_label_comparison(
        self,
        *,
        comparison: ComparisonIR,
        observable: OutputObservableExpressionIR,
        literal: object,
        observable_on_left: bool,
        output: ClassificationOutputSchema,
        positive_polarity: bool,
    ) -> _LogicalResult:
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

        canonical_op = self._canonical_label_operator(
            source_op=comparison.op,
            is_positive_label=is_positive,
        )
        quantity = self._quantity(observable)
        threshold = self._threshold_constant(Decimal(0), source_lexeme="0")
        canonical = ComparisonIR(left=quantity, op=canonical_op, right=threshold)
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
            semantic_profile_id=self.profile_id,
            semantic_profile_version=self.version,
            transformation_id=self.label_transformation_id,
            transformation_version=self.label_transformation_version,
            canonical_constraint=CanonicalConstraintEvidence(
                quantity_kind=quantity.quantity_kind.value,
                operator=canonical_op,
                threshold="0",
                threshold_dtype=EnumDataType.FLOAT,
            ),
            boundary_policy=self._boundary_policy(output),
            compatibility_classification=CompatibilityClassification.EXACT,
            permitted_conclusions=_ALL_CONCLUSIONS,
        )
        return _LogicalResult(expression=canonical, evidence=(evidence,))

    def _lower_probability_comparison(
        self,
        *,
        comparison: ComparisonIR,
        observable: OutputObservableExpressionIR,
        literal: object,
        observable_on_left: bool,
        output: ClassificationOutputSchema,
        positive_polarity: bool,
        in_restriction: bool,
    ) -> _LogicalResult:
        if not output.probability_available:
            raise UnsupportedObservableLoweringError(
                "The selected classification output does not expose probabilities"
            )
        if observable.label is None:
            raise InvalidModelSemanticProfileError(
                "Class-probability IR is missing its selected label"
            )
        numeric_literal = self._numeric_literal(literal)
        if numeric_literal is None:
            raise UnsupportedObservableLoweringError(
                "Class-probability properties require a numeric literal threshold"
            )
        literal_value, literal_dtype, literal_lexeme = numeric_literal
        if isinstance(literal_value, bool) or literal_dtype not in {
            EnumDataType.INT,
            EnumDataType.FLOAT,
        }:
            raise UnsupportedObservableLoweringError(
                "Class-probability thresholds must be numeric literals"
            )
        if comparison.op not in _ORDER_OPERATORS:
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
            comparison.op
            if observable_on_left
            else self._reverse_comparison(comparison.op)
        )
        negative_label, positive_label = output.labels
        selected_label = observable.label.value
        if selected_label == positive_label:
            oriented_interval = interval
            canonical_op = normalized_op
            exact_expression = interval.expression
        elif selected_label == negative_label:
            oriented_interval = interval.negated()
            canonical_op = self._reverse_comparison(normalized_op)
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
        quantity = self._quantity(observable)
        threshold = self._threshold_constant(
            selected_threshold,
            source_lexeme=threshold_text,
        )
        canonical = ComparisonIR(left=quantity, op=canonical_op, right=threshold)

        classification = (
            CompatibilityClassification.EXACT
            if interval.exact
            else CompatibilityClassification.SOUND_UNDER_APPROXIMATION
        )
        permitted = (
            _ALL_CONCLUSIONS if interval.exact else _APPROXIMATE_PROBABILITY_CONCLUSIONS
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
            semantic_profile_id=self.profile_id,
            semantic_profile_version=self.version,
            transformation_id=self.probability_transformation_id,
            transformation_version=self.probability_transformation_version,
            canonical_constraint=CanonicalConstraintEvidence(
                quantity_kind=quantity.quantity_kind.value,
                operator=canonical_op,
                threshold=threshold_text,
                threshold_dtype=EnumDataType.FLOAT,
                exact_threshold_expression=exact_expression,
                threshold_lower_bound=format(oriented_interval.lower, "f"),
                threshold_upper_bound=format(oriented_interval.upper, "f"),
                selected_bound=selected_bound,
                precision_digits=oriented_interval.precision_digits,
                working_precision_digits=(oriented_interval.working_precision_digits),
                guard_digits=oriented_interval.guard_digits,
            ),
            boundary_policy=self._boundary_policy(output),
            compatibility_classification=classification,
            permitted_conclusions=permitted,
        )
        return _LogicalResult(expression=canonical, evidence=(evidence,))

    def _quantity(
        self, observable: OutputObservableExpressionIR
    ) -> ModelQuantityExpressionIR:
        return self._quantity_from_evaluation(observable.evaluation)

    def _quantity_from_evaluation(
        self, evaluation: ModelEvaluationIR
    ) -> ModelQuantityExpressionIR:
        return ModelQuantityExpressionIR(
            evaluation=evaluation,
            quantity_kind=EnumModelQuantityKind.ORIENTED_DECISION_VALUE,
            semantic_profile_id=self.profile_id,
        )

    @staticmethod
    def _threshold_constant(
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

    @staticmethod
    def _numeric_literal(
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

    @staticmethod
    def _canonical_label_operator(
        *,
        source_op: EnumComparisonOperator,
        is_positive_label: bool,
    ) -> EnumComparisonOperator:
        equality = source_op is EnumComparisonOperator.EQ
        predicts_positive = equality if is_positive_label else not equality
        return (
            EnumComparisonOperator.GT
            if predicts_positive
            else EnumComparisonOperator.LTE
        )

    @staticmethod
    def _reverse_comparison(
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

    @staticmethod
    def _boundary_policy(
        output: ClassificationOutputSchema,
    ) -> BoundaryPolicyEvidence:
        negative_label, _positive_label = output.labels
        return BoundaryPolicyEvidence(
            positive_operator=EnumComparisonOperator.GT,
            positive_threshold="0",
            equality_label=negative_label,
        )

    @staticmethod
    def _validated_output(schema: ModelSchema) -> ClassificationOutputSchema:
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
