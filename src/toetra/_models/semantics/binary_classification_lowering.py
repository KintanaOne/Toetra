from __future__ import annotations

from dataclasses import replace

from toetra._compiler.ir.ir1.nodes import (
    AndIR,
    ComparisonIR,
    ImplyIR,
    LogicalIR,
    NotIR,
    OrIR,
    ProblemIR,
    QueryIR,
    RestrictionIR,
    VerificationTask,
)
from toetra._compiler.ir.ir1.outputs import OutputObservableExpressionIR
from toetra._compiler.ir.ir1.scalar import iter_scalar_expressions
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.schema.output_schema import (
    ClassificationOutputSchema,
    EnumOutputObservable,
)
from toetra._models.semantics.base import LoweredVerificationTask
from toetra._models.semantics.binary_classification_common import (
    BinaryClassificationLoweringProfile,
    LogicalLoweringResult,
    validated_output,
)
from toetra._models.semantics.binary_classification_labels import (
    lower_label_comparison,
)
from toetra._models.semantics.binary_classification_pairwise import (
    lower_pairwise_observable_comparison,
    lower_problem,
)
from toetra._models.semantics.binary_classification_probability import (
    lower_probability_comparison,
)
from toetra._models.semantics.errors import UnsupportedObservableLoweringError
from toetra._models.semantics.evidence import SemanticLoweringEvidence


def lower_binary_classification_task(
    task: VerificationTask,
    *,
    schema: ModelSchema,
    profile: BinaryClassificationLoweringProfile,
) -> LoweredVerificationTask:
    output = validated_output(schema)
    query_result = _lower_logical(
        task.query.expression,
        output=output,
        profile=profile,
        positive_polarity=True,
        in_restriction=False,
    )

    scope = task.scope
    restriction_evidence: tuple[SemanticLoweringEvidence, ...] = ()
    if scope.restriction is not None:
        restriction_result = _lower_logical(
            scope.restriction.expression,
            output=output,
            profile=profile,
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
    node: LogicalIR,
    *,
    output: ClassificationOutputSchema,
    profile: BinaryClassificationLoweringProfile,
    positive_polarity: bool,
    in_restriction: bool,
) -> LogicalLoweringResult:
    if isinstance(node, ComparisonIR):
        return _lower_comparison(
            node,
            output=output,
            profile=profile,
            positive_polarity=positive_polarity,
            in_restriction=in_restriction,
        )

    if isinstance(node, ProblemIR):
        return lower_problem(
            node,
            output=output,
            profile=profile,
            positive_polarity=positive_polarity,
        )

    if isinstance(node, AndIR):
        results = tuple(
            _lower_logical(
                operand,
                output=output,
                profile=profile,
                positive_polarity=positive_polarity,
                in_restriction=in_restriction,
            )
            for operand in node.operands
        )
        return LogicalLoweringResult(
            expression=AndIR([result.expression for result in results]),
            evidence=tuple(item for result in results for item in result.evidence),
        )

    if isinstance(node, OrIR):
        results = tuple(
            _lower_logical(
                operand,
                output=output,
                profile=profile,
                positive_polarity=positive_polarity,
                in_restriction=in_restriction,
            )
            for operand in node.operands
        )
        return LogicalLoweringResult(
            expression=OrIR([result.expression for result in results]),
            evidence=tuple(item for result in results for item in result.evidence),
        )

    if isinstance(node, NotIR):
        result = _lower_logical(
            node.operand,
            output=output,
            profile=profile,
            positive_polarity=not positive_polarity,
            in_restriction=in_restriction,
        )
        return LogicalLoweringResult(
            expression=NotIR(result.expression),
            evidence=result.evidence,
        )

    if isinstance(node, ImplyIR):
        left = _lower_logical(
            node.left,
            output=output,
            profile=profile,
            positive_polarity=not positive_polarity,
            in_restriction=in_restriction,
        )
        right = _lower_logical(
            node.right,
            output=output,
            profile=profile,
            positive_polarity=positive_polarity,
            in_restriction=in_restriction,
        )
        return LogicalLoweringResult(
            expression=ImplyIR(left=left.expression, right=right.expression),
            evidence=left.evidence + right.evidence,
        )

    return LogicalLoweringResult(expression=node)


def _lower_comparison(
    comparison: ComparisonIR,
    *,
    output: ClassificationOutputSchema,
    profile: BinaryClassificationLoweringProfile,
    positive_polarity: bool,
    in_restriction: bool,
) -> LogicalLoweringResult:
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
        return LogicalLoweringResult(expression=comparison)

    if left_observable and right_observable:
        assert isinstance(comparison.left, OutputObservableExpressionIR)
        assert isinstance(comparison.right, OutputObservableExpressionIR)
        return lower_pairwise_observable_comparison(
            comparison=comparison,
            left=comparison.left,
            right=comparison.right,
            output=output,
            profile=profile,
            positive_polarity=positive_polarity,
        )

    observable = comparison.left if left_observable else comparison.right
    literal = comparison.right if left_observable else comparison.left
    assert isinstance(observable, OutputObservableExpressionIR)

    if observable.observable is EnumOutputObservable.CLASS_PROBABILITY:
        return lower_probability_comparison(
            comparison=comparison,
            observable=observable,
            literal=literal,
            observable_on_left=left_observable,
            output=output,
            profile=profile,
            positive_polarity=positive_polarity,
            in_restriction=in_restriction,
        )
    if observable.observable is EnumOutputObservable.PREDICTED_LABEL:
        return lower_label_comparison(
            comparison=comparison,
            observable=observable,
            literal=literal,
            observable_on_left=left_observable,
            output=output,
            profile=profile,
            positive_polarity=positive_polarity,
        )
    raise UnsupportedObservableLoweringError(
        f"Unsupported output observable {observable.observable.value!r}"
    )
