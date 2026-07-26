from __future__ import annotations

from toetra._compiler.builder.program import parse_program
from toetra._compiler.parser.parser import parse_toetra_code
from toetra._compiler.semantic.core.validator import ToetraValidator
from toetra._compiler.semantic.runtime.tracer import ValidationTracer
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema


def numeric_schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        task="regression",
        target="score",
        target_dtype=EnumDataType.FLOAT,
        features={
            "a": FeatureSchema(
                name="a",
                dtype=EnumDataType.FLOAT,
                nullable=False,
            ),
            "b": FeatureSchema(
                name="b",
                dtype=EnumDataType.INT,
                nullable=False,
            ),
        },
        metadata={},
    )


def parse_and_validate(source: str, *, with_schema: bool = True):
    program = parse_program(parse_toetra_code(source))
    ToetraValidator().validate(
        program,
        tracer=ValidationTracer(enabled=False),
        model_schema=numeric_schema() if with_schema else None,
    )
    return program


def inline_anchor(name: str = "x0") -> str:
    return f"""
    anchor {name} := {{
        a: 1.0,
        b: 2
    }}
    """
