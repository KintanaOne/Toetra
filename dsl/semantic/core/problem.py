from dsl.language.vocabulary.functions import EnumFunction
from dsl.language.vocabulary.problems import EnumProblem
from dsl.semantic.rules.compatibility import PROBLEM_FUNCTION_COMPATIBILITY
from dsl.semantic.errors.errors import (
    IncompatibleFunctionError,
    InvalidPropertyError,
)
from dsl.semantic.runtime.annotations import SemanticAnnotations
from dsl.semantic.runtime.tracer import ValidationTracer
from model.schema.output_schema import (
    ClassificationOutputSchema,
    EnumOutputObservable,
)


class ProblemValidator:
    """Validate compatibility and semantic sugar for problem-level functions."""

    def __init__(self, tracer=None):
        self.tracer = tracer or ValidationTracer()

    def validate(self, node, *, context=None, model_schema=None):
        self.tracer.log(f"Validating ProblemValidator: {node}")
        problem = self._normalize_problem(node.problem)
        function = self._normalize_function(node.function, problem)
        allowed = PROBLEM_FUNCTION_COMPATIBILITY.get(problem)
        if allowed is None:
            raise IncompatibleFunctionError(f"Unknown problem '{problem.value}'")
        if function not in allowed:
            raise IncompatibleFunctionError(
                f"{function.value} not allowed for {problem.value}"
            )
        if problem is EnumProblem.CLASSIFICATION and function is EnumFunction.EQUAL:
            self._validate_classification_equal(
                node, context=context, model_schema=model_schema
            )
        return True

    @staticmethod
    def _validate_classification_equal(node, *, context, model_schema) -> None:
        if context is None:
            raise InvalidPropertyError(
                "CLASSIFICATION.EQUAL() requires a resolved semantic context"
            )
        points = context.point_environment.all()
        if len(points) != 2:
            names = ", ".join(point.name for point in points) or "none"
            raise InvalidPropertyError(
                "CLASSIFICATION.EQUAL() requires exactly two visible model-input "
                f"points, got {len(points)}: [{names}]"
            )
        if not context.model_identity or not context.model_target:
            raise InvalidPropertyError(
                "CLASSIFICATION.EQUAL() requires declared model and output identities"
            )
        if model_schema is not None:
            output = model_schema.output_schema
            if not isinstance(output, ClassificationOutputSchema):
                raise InvalidPropertyError(
                    "CLASSIFICATION.EQUAL() requires a classification output schema"
                )
            if EnumOutputObservable.PREDICTED_LABEL not in output.available_observables:
                raise InvalidPropertyError(
                    "CLASSIFICATION.EQUAL() requires predicted-label observability"
                )
            if len(output.labels) != 2:
                raise InvalidPropertyError(
                    "The initial CLASSIFICATION.EQUAL() profile requires exactly "
                    "two ordered labels"
                )
        evaluations = tuple(
            context.evaluation_registry.intern(
                model_identity=context.model_identity,
                point=point,
                output_name=context.model_target,
            )
            for point in points
        )
        if node.semantic is None:
            node.semantic = SemanticAnnotations()
        node.semantic.resolved_evaluations = evaluations

    def _normalize_problem(self, problem) -> EnumProblem:
        if isinstance(problem, EnumProblem):
            return problem
        try:
            return EnumProblem.from_str(str(problem))
        except ValueError as e:
            raise IncompatibleFunctionError(f"Unknown problem '{problem}'") from e

    def _normalize_function(self, function, problem: EnumProblem) -> EnumFunction:
        if function is None:
            raise IncompatibleFunctionError(
                f"Missing function for problem '{problem.value}'"
            )
        if isinstance(function, EnumFunction):
            return function
        try:
            return EnumFunction.from_str(str(function))
        except ValueError as e:
            raise IncompatibleFunctionError(f"Unknown function '{function}'") from e
