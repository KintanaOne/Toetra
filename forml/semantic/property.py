from forml.semantic.implication import ImplicationValidator
from forml.semantic.errors import InvalidPropertyError, SemanticError
from forml.semantic.tracer import ValidationTracer


class PropertyValidator:

    def __init__(self, tracer=None):
        self.tracer = tracer or ValidationTracer()

    def validate(self, prop):
        self.tracer.log(f"Validating Property: {prop.type}")

        # ---------------------------
        # 1. Base verification
        # ---------------------------
        if not hasattr(prop, "implication") or prop.implication is None:
            raise InvalidPropertyError(
                message="Missing implication",
                node=prop,
                context="PropertyValidator"
            )

        # ---------------------------
        # 2. implication Validation 
        # ---------------------------
        try:
            ImplicationValidator(tracer=self.tracer).validate(prop.implication)

        except SemanticError as e:
            # Enrichir le contexte
            raise InvalidPropertyError(
                message=f"Property '{prop.type}' invalid: {e}",
                node=prop,
                context="PropertyValidator"
            ) from e

        # ---------------------------
        # 3. Succees
        # ---------------------------
        self.tracer.log(f"✔ Property '{prop.type}' validated")

        return True