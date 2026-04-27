from dsl.semantic.implication import ImplicationValidator
from dsl.semantic.errors import InvalidPropertyError, SemanticError
from dsl.semantic.tracer import ValidationTracer


class PropertyValidator:

    def __init__(self, tracer=None):
        self.tracer = tracer or ValidationTracer()

    def validate(self, prop):
        self.tracer.log(f"Validating Property: {prop.type}")

        if not hasattr(prop, "rule") or prop.rule is None:
            raise InvalidPropertyError(
                message="Missing rule",
                node=prop,
                context="PropertyValidator"
            )

        rule = prop.rule
        scope = rule.scope              # LHS
        assertion = rule.assertion      # AssertionNode
        root = assertion.root           # LogicalNode

        try:
            ImplicationValidator(tracer=self.tracer).validate(scope, root)

        except SemanticError as e:
            raise InvalidPropertyError(
                message=f"Property '{prop.type}' invalid: {e}",
                node=prop,
                context="PropertyValidator"
            ) from e

        self.tracer.log(f"✔ Property '{prop.type}' validated")
        return True