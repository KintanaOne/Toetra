from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from toetra._compatibility.descriptors import (
    FrameworkModelDescriptor,
    NumericSemanticDescriptor,
)
from toetra._compatibility.enums import NumericFamily
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.schema.output_schema import ClassificationOutputSchema
from toetra._models.families import BINARY_LOGISTIC_AFFINE_MODEL_FAMILY


def framework_model_descriptor(schema: ModelSchema) -> FrameworkModelDescriptor:
    """Return explicit source-model compatibility metadata or a safe fallback."""

    if schema.compatibility is not None:
        return schema.compatibility

    metadata = schema.metadata_by_name
    parameter_dtypes = _parameter_dtypes(metadata)
    numeric_semantics, profile_id = _numeric_semantics(parameter_dtypes)
    return FrameworkModelDescriptor(
        framework_adapter_id=schema.framework.value,
        framework_version=_optional_text(metadata.get("framework_version")),
        model_family=_model_family(schema),
        source_execution_profile_id=profile_id,
        numeric_semantics=numeric_semantics,
        parameter_dtypes=parameter_dtypes,
        input_dtypes=tuple(
            feature.source_dtype or feature.dtype.value for feature in schema.features
        ),
        output_dtype=(schema.output_schema.source_dtype or _output_dtype(schema)),
    )


def _model_family(schema: ModelSchema) -> str:
    if schema.model_type == "LinearRegression" and schema.task == "regression":
        return "affine_regression"
    if (
        schema.model_type == "LogisticRegression"
        and schema.task == "classification"
        and isinstance(schema.output_schema, ClassificationOutputSchema)
        and schema.output_schema.decision_policy is not None
    ):
        return BINARY_LOGISTIC_AFFINE_MODEL_FAMILY
    return f"unknown:{schema.task}:{schema.model_type}"


def _parameter_dtypes(metadata: Mapping[str, Any]) -> tuple[str, ...]:
    linear = metadata.get("linear")
    if not isinstance(linear, Mapping):
        return ()

    declared = (
        linear.get("coef_source_dtype"),
        linear.get("intercept_source_dtype"),
    )
    values = tuple(str(value) for value in declared if value)
    if values:
        return tuple(dict.fromkeys(values))

    inferred: list[str] = []
    for key in ("coef", "intercept"):
        inferred.extend(_infer_dtype_names(linear.get(key)))
    return tuple(dict.fromkeys(inferred))


def _infer_dtype_names(value: Any) -> list[str]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        result: list[str] = []
        for item in value:
            result.extend(_infer_dtype_names(item))
        return result
    if isinstance(value, bool):
        return ["python.bool"]
    if isinstance(value, int):
        return ["python.int"]
    if isinstance(value, float):
        return ["python.float"]
    if value is None:
        return []
    return [type(value).__name__]


def _numeric_semantics(
    dtypes: tuple[str, ...],
) -> tuple[NumericSemanticDescriptor, str]:
    normalized = {value.lower() for value in dtypes}
    if normalized and all("float64" in value for value in normalized):
        return NumericSemanticDescriptor.binary_float(64), "ieee754_binary64"
    if normalized and all("float32" in value for value in normalized):
        return NumericSemanticDescriptor.binary_float(32), "ieee754_binary32"
    if any("float" in value for value in normalized):
        return (
            NumericSemanticDescriptor.binary_float(None),
            "binary_float_unknown_width",
        )
    if normalized and all("int" in value for value in normalized):
        return (
            NumericSemanticDescriptor(
                family=NumericFamily.INTEGER,
                precision="exact_or_source_defined",
            ),
            "integer_source_defined",
        )
    return NumericSemanticDescriptor.unknown(), "unknown"


def _output_dtype(schema: ModelSchema) -> str | None:
    dtype = schema.output_schema.primary_dtype
    return dtype.value if dtype is not None else None


def _optional_text(value: object) -> str | None:
    return str(value) if value is not None else None
