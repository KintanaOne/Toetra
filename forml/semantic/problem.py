from forml.language.vocabulary.functions import EnumFunction
from forml.semantic.compatibility import PROBLEM_FUNCTION_COMPATIBILITY
from forml.semantic.errors import InvalidPropertyError
from forml.semantic.tracer import ValidationTracer
from forml.semantic_.errors import IncompatibleFunctionError


class ProblemValidator:

    def __init__(self, tracer=None):
        self.tracer = tracer or ValidationTracer()

    def validate(self, node):
        self.tracer.log(f"Validating ProblemValidator: {node}")

        problem = node.problem.upper()
        function_str = node.function

        # 🔥 conversion string → Enum
        try:
            function = EnumFunction[function_str]
        except KeyError:
            raise IncompatibleFunctionError(
                f"Unknown function '{function_str}'"
            )

        allowed = PROBLEM_FUNCTION_COMPATIBILITY.get(problem)

        if not allowed:
            raise IncompatibleFunctionError(
                f"Unknown problem '{problem}'"
            )

        if function not in allowed:
            raise IncompatibleFunctionError(
                f"{function_str} not allowed for {problem}"
            )