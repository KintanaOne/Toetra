from dsl.semantic.errors import InvalidPropertyError, SemanticError
from dsl.semantic.tracer import ValidationTracer

from dsl.semantic.binding import BindingValidator
from dsl.semantic.logic import LogicValidator


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
        scope = rule.scope
        assertion = rule.assertion
        root = assertion.root

        print(f"SCOPE : {scope}")

        try:
            # ------------------------------------------------------------------
            # 1. LHS validation (context creation)
            # ------------------------------------------------------------------
            context = scope 

            # ------------------------------------------------------------------
            # 2. Binding phase (variable resolution)
            # ------------------------------------------------------------------
            BindingValidator(tracer=self.tracer).validate(
                context,
                root
            )

            # ------------------------------------------------------------------
            # 3. Logic validation (structure check only)
            # ------------------------------------------------------------------
            LogicValidator(tracer=self.tracer).validate(
                root,
                context
            )

        except SemanticError as e:
            raise InvalidPropertyError(
                message=f"Property '{prop.type}' invalid: {e}",
                node=prop,
                context="PropertyValidator"
            ) from e

        self.tracer.log(f"✔ Property '{prop.type}' validated")
        return True