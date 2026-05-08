from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from dsl.semantic.runtime.tracer import ValidationTracer

from dsl.semantic.core.property import PropertyValidator
from test.fixtures.properties_samples import (
    VALID_MINIMAL_AT,
    VALID_MINIMAL_CHECK_AT,
    VALID_MINIMAL_EXISTS,
    VALID_MINIMAL_FORALL,
    VALID_MINIMAL_PAIRWISE
)

class FORMLValidator:

    def __init__(self):
        self.tracer = ValidationTracer(enabled=True)

    def validate(self, program, tracer=None):
        if tracer:
            self.tracer = tracer

        self.tracer.log(f"Validating FORMLValidator: {program}")

        for prop in program.body:
            PropertyValidator(tracer=self.tracer).validate(prop)

        return True


if __name__ == "__main__":
    """ This script is for quick testing of the validator. It parses a sample property and prints the resulting AST than validates it """
    CST = parse_forml_code(VALID_MINIMAL_AT)
    print(CST.pretty())

    AST = parse_program(CST)
    print(AST)

    tracer = ValidationTracer(enabled=True)
    validator = FORMLValidator()
    validator.validate(AST, tracer=tracer)