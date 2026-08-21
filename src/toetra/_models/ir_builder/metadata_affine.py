from __future__ import annotations

from collections.abc import Mapping, Sequence
from numbers import Real
from typing import Any, cast

from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.ir.affine import AffineModelIR
from toetra._models.ir_builder.errors import (
    InvalidModelIRParameterError,
    MissingModelIRParameterError,
    UnsupportedModelIRBuilderError,
)
from toetra._models.schema.model_schema import ModelSchema


class MetadataAffineModelIRBuilder:
    """Build affine Model IR from the legacy normalized metadata contract.

    This builder preserves schema-only execution while artifact-backed runtime
    paths construct Model IR directly from the fitted framework model. Generic
    metadata is therefore a compatibility input, not the default computational
    source of truth.
    """

    supported_model_types = frozenset({"LinearRegression", "LogisticRegression"})

    def build(self, schema: ModelSchema) -> AffineModelIR:
        self._validate_schema(schema)
        linear = self._linear_metadata(schema)
        feature_names = self._feature_names(schema, linear)
        coefficients = self._coefficients(schema, linear)
        bias = self._bias(schema, linear)

        if len(coefficients) != len(feature_names):
            raise InvalidModelIRParameterError(
                "Affine coefficient count does not match schema feature count: "
                f"{len(coefficients)} != {len(feature_names)}."
            )

        try:
            return AffineModelIR(
                terms=tuple(zip(feature_names, coefficients, strict=True)),
                bias=bias,
            )
        except (TypeError, ValueError) as error:
            raise InvalidModelIRParameterError(str(error)) from error

    def _validate_schema(self, schema: ModelSchema) -> None:
        if not isinstance(schema, ModelSchema):
            raise TypeError("schema must be a ModelSchema.")
        if schema.framework is not EnumModelFramework.SKLEARN:
            raise UnsupportedModelIRBuilderError(
                "Legacy affine metadata construction supports sklearn schemas only."
            )
        if schema.model_type not in self.supported_model_types:
            raise UnsupportedModelIRBuilderError(
                "No affine metadata Model IR builder for "
                f"model_type={schema.model_type!r}."
            )

    @staticmethod
    def _linear_metadata(schema: ModelSchema) -> Mapping[str, Any]:
        raw = schema.get_metadata("linear")
        if not isinstance(raw, Mapping):
            raise MissingModelIRParameterError(
                "ModelSchema metadata must contain affine 'linear' parameters."
            )
        if "coef" not in raw or "intercept" not in raw:
            raise MissingModelIRParameterError(
                "Affine metadata must contain 'coef' and 'intercept'."
            )
        return raw

    @staticmethod
    def _feature_names(
        schema: ModelSchema,
        linear: Mapping[str, Any],
    ) -> tuple[str, ...]:
        raw = linear.get("feature_names")
        if raw is None:
            return schema.feature_names
        if not _is_sequence(raw):
            raise InvalidModelIRParameterError(
                "linear.feature_names must be a sequence of strings."
            )

        names = tuple(cast(Sequence[Any], raw))
        if not all(isinstance(name, str) for name in names):
            raise InvalidModelIRParameterError(
                "linear.feature_names must contain only strings."
            )
        typed_names = cast(tuple[str, ...], names)
        if typed_names != schema.feature_names:
            raise InvalidModelIRParameterError(
                "Affine metadata feature order must match ModelSchema.feature_names."
            )
        return typed_names

    def _coefficients(
        self,
        schema: ModelSchema,
        linear: Mapping[str, Any],
    ) -> tuple[float, ...]:
        raw = linear["coef"]
        if not _is_sequence(raw):
            raise InvalidModelIRParameterError(
                "linear.coef must be a coefficient sequence."
            )
        values = cast(Sequence[Any], raw)

        if schema.model_type == "LogisticRegression":
            if len(values) != 1 or not _is_sequence(values[0]):
                raise InvalidModelIRParameterError(
                    "Binary logistic coefficients must contain exactly one row."
                )
            values = cast(Sequence[Any], values[0])
        elif values and _is_sequence(values[0]):
            if len(values) != 1:
                raise InvalidModelIRParameterError(
                    "Only single-output affine coefficients are supported."
                )
            values = cast(Sequence[Any], values[0])

        return tuple(
            _normalize_real(value, field_name="Affine coefficients") for value in values
        )

    def _bias(
        self,
        schema: ModelSchema,
        linear: Mapping[str, Any],
    ) -> float:
        raw = linear["intercept"]
        if schema.model_type == "LogisticRegression":
            if not _is_sequence(raw) or len(cast(Sequence[Any], raw)) != 1:
                raise InvalidModelIRParameterError(
                    "Binary logistic intercept must contain exactly one value."
                )
            raw = cast(Sequence[Any], raw)[0]
        elif _is_sequence(raw):
            values = cast(Sequence[Any], raw)
            if len(values) != 1 or _is_sequence(values[0]):
                raise InvalidModelIRParameterError(
                    "Only a single affine intercept is supported."
                )
            raw = values[0]
        return _normalize_real(raw, field_name="The affine intercept")


def _is_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes))


def _normalize_real(value: Any, *, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise InvalidModelIRParameterError(
            f"{field_name} must contain real numeric values."
        )
    return float(value)
