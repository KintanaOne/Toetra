from dsl.language.vocabulary.functions import EnumFunction
from dsl.language.vocabulary.problems import EnumProblem
from dsl.semantic.rules.compatibility import PROBLEM_FUNCTION_COMPATIBILITY
from dsl.semantic.errors.errors import IncompatibleFunctionError
from dsl.semantic.runtime.tracer import ValidationTracer


class ProblemValidator:
    """
    Validate compatibility between a problem family and a problem-level function.

    Examples:
        CLASSIFICATION.EQUAL()
        REGRESSION.BETWEEN()
    """

    def __init__(self, tracer=None):
        self.tracer = tracer or ValidationTracer()

    def validate(self, node):
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

        return True

    def _normalize_problem(self, problem) -> EnumProblem:
        if isinstance(problem, EnumProblem):
            return problem

        try:
            return EnumProblem.from_str(str(problem))
        except ValueError as e:
            raise IncompatibleFunctionError(f"Unknown problem '{problem}'") from e

    def _normalize_function(
        self,
        function,
        problem: EnumProblem,
    ) -> EnumFunction:
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
