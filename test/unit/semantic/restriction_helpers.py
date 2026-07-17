from __future__ import annotations

from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from dsl.semantic.core.validator import FORMLValidator
from dsl.semantic.runtime.tracer import ValidationTracer
from dsl.semantic.types.enums import EnumDataType
from model.detector.model_framework import EnumModelFramework
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema


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
    program = parse_program(parse_forml_code(source))
    FORMLValidator().validate(
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
