from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn import __version__ as sklearn_version
from sklearn.linear_model import LinearRegression

from toetra._compatibility.enums import NumericFamily
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.compatibility import framework_model_descriptor
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.introspector.sklearn_introspector import SklearnIntrospector
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema


def test_sklearn_introspector_preserves_framework_and_dtype_profile(tmp_path) -> None:
    frame = pd.DataFrame(
        {
            "a": np.asarray([0.0, 1.0, 2.0], dtype=np.float32),
            "score": np.asarray([1.0, 3.0, 5.0], dtype=np.float32),
        }
    )
    model = LinearRegression().fit(frame[["a"]], frame["score"])
    dataset = tmp_path / "regression.csv"
    frame.to_csv(dataset, index=False)

    schema = SklearnIntrospector(
        model, source_path=dataset, target_name="score"
    ).introspect()
    descriptor = framework_model_descriptor(schema)

    assert descriptor.framework_adapter_id == "sklearn"
    assert descriptor.framework_version == sklearn_version
    assert descriptor.model_family == "affine_regression"
    assert descriptor.parameter_dtypes == ("float32",)
    assert descriptor.numeric_semantics.family is NumericFamily.BINARY_FLOAT
    assert descriptor.numeric_semantics.width_bits == 32
    assert schema.features["a"].source_dtype == "float64"
    assert schema.target_source_dtype == "float64"


def test_manual_schema_gets_a_conservative_derived_profile() -> None:
    schema = ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={
            "a": FeatureSchema(
                name="a", dtype=EnumDataType.FLOAT, source_dtype="float32"
            )
        },
        target="score",
        task="regression",
        metadata={
            "linear": {
                "coef": [2.0],
                "intercept": 1.0,
                "feature_names": ["a"],
            }
        },
    )

    descriptor = framework_model_descriptor(schema)

    assert descriptor.model_family == "affine_regression"
    assert descriptor.source_execution_profile_id == "binary_float_unknown_width"
    assert descriptor.input_dtypes == ("float32",)
