from pathlib import Path

from forml.transformer.nodes import ProblemExpr
from forml.transformer.transformer import transform_forml_code
from forml.semantic.compatibility import (
    PROBLEM_FUNCTION_COMPATIBILITY,
    PROPERTY_SCOPE_COMPATIBILITY,
)
from forml.semantic.scope import get_scope_from_property
from forml.semantic.errors import (
    IncompatibleFunctionError,
    InvalidPropertyError,
)


class FORMLValidator:

    def validate(self, program):
        self.validate_body(program.body)

    # ────────────────────────────── BODY ──────────────────────────────

    def validate_body(self, body):
        for section in body.sections:
            if hasattr(section, "property"):
                self.validate_property(section.property)

    # ────────────────────────────── PROPERTY ──────────────────────────

    def validate_property(self, prop):
        if not prop.assertion:
            raise InvalidPropertyError("Property missing assertion.")

        expr = prop.assertion.expr

        # 1️⃣ Validate problem/function
        if isinstance(expr, ProblemExpr):
            self.validate_problem_expr(expr)

        # 2️⃣ Extract semantic scope 🔥
        scope = get_scope_from_property(prop)

        if not scope:
            raise InvalidPropertyError(
                f"Cannot determine semantic scope for property '{prop.property_type}'"
            )

        # 3️⃣ Validate property ↔ scope 🔥
        self.validate_property_scope(prop.property_type, scope)

    # ────────────────────────────── SCOPE ─────────────────────────────

    def validate_property_scope(self, property_type, scope):
        allowed = PROPERTY_SCOPE_COMPATIBILITY.get(property_type.upper(), set())

        if scope not in allowed:
            raise InvalidPropertyError(
                f"Property '{property_type}' incompatible with scope '{scope.value}'"
            )

    # ────────────────────────────── PROBLEM ───────────────────────────

    def validate_problem_expr(self, expr):
        problem = expr.problem.upper()
        function = expr.function.function

        allowed = PROBLEM_FUNCTION_COMPATIBILITY.get(problem)

        if not allowed:
            raise IncompatibleFunctionError(f"Unknown problem '{problem}'.")

        if function not in allowed:
            raise IncompatibleFunctionError(
                f"Function '{function}' not allowed for problem '{problem}'."
            )

if __name__ == "__main__":

    test_path = Path(__file__).parent.parent / "example/00_simple_correct_example_multi_comment.forml"
    print(test_path)
    if test_path.exists():
        with open(test_path, "r", encoding="utf-8") as f:
            code = f.read()
    program = transform_forml_code(code)
    validator = FORMLValidator()
    validator.validate(program)
    print("Validation successful!")