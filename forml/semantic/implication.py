from forml.semantic.lhs import LHSValidator
from forml.semantic.logic import LogicValidator
from forml.semantic.problem import ProblemValidator
from forml.semantic.binding import BindingValidator
from forml.semantic.errors import InvalidPropertyError
from forml.semantic.tracer import ValidationTracer


class ImplicationValidator:

    def __init__(self, tracer=None):
        self.tracer = tracer or ValidationTracer()

    def validate(self, imp):
        self.tracer.log(f"Validating ImplicationNode: {imp}")

        lhs = imp.left
        rhs = imp.right

        # ---------------------------
        # 1. LHS → create contexte
        # ---------------------------
        lhs_validator = LHSValidator(tracer=self.tracer)
        context = lhs_validator.validate(lhs)

        # ---------------------------
        # 2. Binding (CRUCIAL)
        # ---------------------------
        BindingValidator(tracer=self.tracer).validate(context, rhs)

        # ---------------------------
        # 3. RHS validation
        # ---------------------------
        node_type = rhs.__class__.__name__

        if node_type in ["ComparisonNode", "AndNode", "OrNode", "NotNode"]:
            LogicValidator(tracer=self.tracer).validate(rhs, context)

        elif node_type == "ProblemNode":
            ProblemValidator().validate(rhs)

        else:
            raise InvalidPropertyError(f"Invalid RHS type: {node_type}")