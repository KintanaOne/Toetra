from dsl.builder.program import parse_program
from dsl.parser.errors import ParserError
from dsl.parser.parser import parse_forml_code
from dsl.semantic.runtime.tracer import ValidationTracer

from dsl.semantic.core.property import PropertyValidator


class FORMLValidator:

    def __init__(self):
        self.tracer = ValidationTracer(enabled=True)

    def validate(self, program, tracer=None, model_schema=None):
        if tracer:
            self.tracer = tracer

        self.tracer.log(f"Validating FORMLValidator: {program}")

        try:
            for prop in program.body:
                PropertyValidator(tracer=self.tracer).validate(
                    prop,
                    model_schema=model_schema,
                )

        except ParserError:
            raise

        except Exception as e:
            raise ParserError(str(e)) from e

        return True


if __name__ == "__main__":
    """This script is for quick testing of the validator. It parses a sample property and prints the resulting AST than validates it"""

    sample = """
    model := "model.onnx"
    target := MyTarget

    [ROBUSTNESS]:
    at x0 => CLASSIFICATION.EQUAL()
    """

    CST = parse_forml_code(sample)
    print(CST.pretty())

    AST = parse_program(CST)
    print(AST)

    tracer = ValidationTracer(enabled=True)
    validator = FORMLValidator()
    validator.validate(AST, tracer=tracer)
