from __future__ import annotations

from dsl.ast.nodes.program import ProgramNode
from dsl.builder.program import parse_program
from dsl.parser.errors import ParserError
from dsl.parser.parser import parse_toetra_code
from dsl.semantic.runtime.tracer import ValidationTracer

from dsl.semantic.core.anchors import AnchorValidator
from dsl.semantic.core.property import PropertyValidator
from dsl.semantic.core.specification_constants import collect_specification_constants

from typing import TYPE_CHECKING, Mapping

if TYPE_CHECKING:
    from dsl.semantic.symbols.point import ResolvedAnchorBinding


class ToetraValidator:

    def __init__(self):
        self.tracer = ValidationTracer(enabled=True)

    def validate(
        self,
        program: ProgramNode,
        tracer=None,
        model_schema=None,
        resolved_anchors: Mapping[str, ResolvedAnchorBinding] | None = None,
    ) -> bool:
        if tracer:
            self.tracer = tracer

        self.tracer.log(f"Validating ToetraValidator: {program}")

        try:
            model_target = program.header.target
            model_identity = program.header.model
            if not model_identity:
                raise ParserError(
                    "Cannot validate a Toetra program without a declared model identity"
                )
            specification_constants = collect_specification_constants(program.header)
            global_points = AnchorValidator(
                model_schema=model_schema,
                resolved_anchors=resolved_anchors,
            ).validate(program.anchors)

            for prop in program.body:
                PropertyValidator(tracer=self.tracer).validate(
                    prop,
                    model_schema=model_schema,
                    model_target=model_target,
                    model_identity=model_identity,
                    specification_constants=specification_constants,
                    global_points=global_points,
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

    CST = parse_toetra_code(sample)
    print(CST.pretty())

    AST = parse_program(CST)
    print(AST)

    tracer = ValidationTracer(enabled=True)
    validator = ToetraValidator()
    validator.validate(AST, tracer=tracer)
