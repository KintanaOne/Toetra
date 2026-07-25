from __future__ import annotations

from dsl.builder.program import parse_program
from dsl.parser.parser import parse_toetra_code
from dsl.semantic.core.validator import ToetraValidator
from dsl.semantic.runtime.tracer import ValidationTracer
from dsl.semantic.types.enums import EnumDataType
from model.detector.model_framework import EnumModelFramework
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema


def anchor_schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={
            "age": FeatureSchema("age", EnumDataType.INT),
            "income": FeatureSchema("income", EnumDataType.FLOAT),
            "active": FeatureSchema("active", EnumDataType.BOOL),
        },
        target="score",
        task="regression",
        target_dtype=EnumDataType.FLOAT,
    )


def build_program(source: str):
    return parse_program(parse_toetra_code(source))


def validate_program(source: str, *, with_schema: bool = True):
    program = build_program(source)
    ToetraValidator().validate(
        program,
        tracer=ValidationTracer(enabled=False),
        model_schema=anchor_schema() if with_schema else None,
    )
    return program
