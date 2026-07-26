from __future__ import annotations

from toetra._compiler.ir.ir2.nodes import VerificationTaskIR2
from toetra._compiler.ir.ir2.run_ir2 import run_ir2_with_model_schema
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema


def linear_schema(*, coefficient: float = 2.0, intercept: float = 1.0) -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={
            "a": FeatureSchema(
                name="a",
                dtype=EnumDataType.FLOAT,
                nullable=False,
            )
        },
        target="score",
        task="regression",
        metadata={
            "linear": {
                "coef": [coefficient],
                "intercept": intercept,
                "feature_names": ["a"],
            }
        },
    )


def build_task(source: str, *, coefficient: float = 2.0) -> VerificationTaskIR2:
    tasks = run_ir2_with_model_schema(
        source,
        schema=linear_schema(coefficient=coefficient),
    )
    assert len(tasks) == 1
    return tasks[0]
