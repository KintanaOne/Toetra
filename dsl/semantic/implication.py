from dsl.semantic.lhs import LHSValidator
from dsl.semantic.logic import LogicValidator
from dsl.semantic.problem import ProblemValidator
from dsl.semantic.binding import BindingValidator
from dsl.semantic.errors import InvalidPropertyError
from dsl.semantic.tracer import ValidationTracer


class ImplicationValidator:

    def __init__(self, tracer=None):
        self.tracer = tracer or ValidationTracer()

    
    def validate(self, scope, rhs):
        self.tracer.log(f"Validating implication with scope={scope} rhs={rhs}")

        # 1. LHS → contexte
        lhs_validator = LHSValidator(tracer=self.tracer)
        context = lhs_validator.validate(scope)

        # 2. Binding
        BindingValidator(tracer=self.tracer).validate(context, rhs)

        # 3. RHS validation
        node_type = rhs.__class__.__name__

        if node_type in ["ComparisonNode", "AndNode", "OrNode", "NotNode"]:
            LogicValidator(tracer=self.tracer).validate(rhs, context)

        elif node_type == "ProblemNode":
            ProblemValidator(tracer=self.tracer).validate(rhs)

        else:
            raise InvalidPropertyError(f"Invalid RHS type: {node_type}")