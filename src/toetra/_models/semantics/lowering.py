from __future__ import annotations

from toetra._compiler.ir.ir1.nodes import (
    AndIR,
    ComparisonIR,
    ImplyIR,
    LogicalIR,
    NotIR,
    OrIR,
    ProblemIR,
    VerificationTask,
)
from toetra._compiler.ir.ir1.outputs import OutputObservableExpressionIR
from toetra._compiler.ir.ir1.scalar import iter_scalar_expressions
from toetra._language.vocabulary.functions import EnumFunction
from toetra._language.vocabulary.problems import EnumProblem
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.semantics.base import LoweredVerificationTask
from toetra._models.semantics.errors import MissingModelSemanticsError
from toetra._models.semantics.registry import (
    ModelSemanticRegistry,
    create_default_model_semantic_registry,
)


class ModelSemanticLowerer:
    """Apply model-family semantics before final NNF normalization."""

    def __init__(self, registry: ModelSemanticRegistry | None = None) -> None:
        self.registry = registry or create_default_model_semantic_registry()

    def lower_task(
        self,
        task: VerificationTask,
        *,
        schema: ModelSchema,
    ) -> LoweredVerificationTask:
        if not task_references_output_observables(task):
            return LoweredVerificationTask(task=task)

        profile = self.registry.resolve(schema)
        result = profile.lower_task(task, schema=schema)
        if task_references_output_observables(result.task):
            raise MissingModelSemanticsError(
                "Model semantic lowering left public output observables in the "
                "canonical verification task"
            )
        return result

    @staticmethod
    def assert_no_unlowered_observables(tasks: list[VerificationTask]) -> None:
        if any(task_references_output_observables(task) for task in tasks):
            raise MissingModelSemanticsError(
                "Output-observable properties require a model schema and a "
                "registered model semantic profile; use "
                "run_ir2_with_model_schema(...)"
            )


def task_references_output_observables(task: VerificationTask) -> bool:
    if _logical_references_output_observables(task.query.expression):
        return True
    restriction = task.scope.restriction
    return restriction is not None and _logical_references_output_observables(
        restriction.expression
    )


def _logical_references_output_observables(node: LogicalIR) -> bool:
    if isinstance(node, ProblemIR):
        return (
            node.problem is EnumProblem.CLASSIFICATION
            and node.function is EnumFunction.EQUAL
        )
    if isinstance(node, ComparisonIR):
        return any(
            isinstance(expression, OutputObservableExpressionIR)
            for root in (node.left, node.right)
            for expression in iter_scalar_expressions(root)
        )
    if isinstance(node, (AndIR, OrIR)):
        return any(
            _logical_references_output_observables(item) for item in node.operands
        )
    if isinstance(node, NotIR):
        return _logical_references_output_observables(node.operand)
    if isinstance(node, ImplyIR):
        return _logical_references_output_observables(
            node.left
        ) or _logical_references_output_observables(node.right)
    return False
