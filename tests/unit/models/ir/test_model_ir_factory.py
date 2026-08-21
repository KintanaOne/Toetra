from __future__ import annotations

from sklearn.linear_model import LinearRegression

from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.ir.affine import AffineModelIR
from toetra._models.ir_builder.factory import ModelIRFactory
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema


def _schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features=(
            FeatureSchema(name="a", dtype=EnumDataType.FLOAT),
            FeatureSchema(name="b", dtype=EnumDataType.FLOAT),
        ),
        output_name="score",
        task="regression",
        metadata={
            "linear": {
                "coef": [1.5, -2.0],
                "intercept": 0.25,
                "feature_names": ["a", "b"],
            }
        },
    )


def test_factory_builds_affine_ir_directly_from_fitted_model() -> None:
    model = LinearRegression().fit([[0.0, 0.0], [1.0, 1.0]], [0.25, -0.25])
    schema = ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features=_schema().features,
        output_name="score",
        task="regression",
        metadata={},
    )

    result = ModelIRFactory().build(model, schema)

    assert isinstance(result, AffineModelIR)
    assert tuple(name for name, _coefficient in result.terms) == ("a", "b")


def test_factory_preserves_schema_only_compatibility_through_model_ir() -> None:
    assert ModelIRFactory().build_from_schema(_schema()) == AffineModelIR(
        terms=(("a", 1.5), ("b", -2.0)),
        bias=0.25,
    )
