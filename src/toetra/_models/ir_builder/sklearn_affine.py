from __future__ import annotations

from collections.abc import Sequence
from numbers import Real
from typing import Any, cast

from sklearn.linear_model import LinearRegression, LogisticRegression

from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.ir.affine import AffineModelIR
from toetra._models.schema.model_schema import ModelSchema

SklearnAffineModel = LinearRegression | LogisticRegression


class SklearnAffineModelIRBuilder:
    """Build a normalized affine computation from supported sklearn models."""

    def build(
        self,
        model: object,
        schema: ModelSchema,
    ) -> AffineModelIR:
        if type(model) not in (LinearRegression, LogisticRegression):
            raise TypeError(
                "SklearnAffineModelIRBuilder requires an exact LinearRegression "
                "or LogisticRegression model."
            )
        if not isinstance(schema, ModelSchema):
            raise TypeError("schema must be a ModelSchema.")
        if schema.framework is not EnumModelFramework.SKLEARN:
            raise ValueError("The affine sklearn builder requires a sklearn schema.")
        if schema.model_type != type(model).__name__:
            raise ValueError(
                "ModelSchema model_type does not match the source model: "
                f"{schema.model_type!r} != {type(model).__name__!r}."
            )

        typed_model = cast(SklearnAffineModel, model)
        coefficients = _single_output_coefficients(typed_model)
        bias = _single_output_bias(typed_model)
        feature_names = schema.feature_names
        _validate_feature_contract(
            model=typed_model,
            feature_names=feature_names,
            coefficient_count=len(coefficients),
        )

        return AffineModelIR(
            terms=tuple(
                (name, coefficient)
                for name, coefficient in zip(
                    feature_names,
                    coefficients,
                    strict=True,
                )
            ),
            bias=bias,
        )


def _single_output_coefficients(model: SklearnAffineModel) -> tuple[float, ...]:
    raw = _required_fitted_attribute(model, "coef_")
    normalized = _to_builtin(raw)
    if not _is_sequence(normalized):
        raise ValueError("A fitted affine model must expose a coefficient sequence.")

    values = cast(Sequence[Any], normalized)
    if values and _is_sequence(values[0]):
        if len(values) != 1:
            raise ValueError(
                "Only single-output affine model coefficients are supported."
            )
        values = cast(Sequence[Any], values[0])
    return tuple(
        _normalize_real(value, field_name="Affine coefficients") for value in values
    )


def _single_output_bias(model: SklearnAffineModel) -> float:
    raw = _required_fitted_attribute(model, "intercept_")
    normalized = _to_builtin(raw)
    if _is_sequence(normalized):
        values = cast(Sequence[Any], normalized)
        if len(values) != 1 or _is_sequence(values[0]):
            raise ValueError("Only a single affine model intercept is supported.")
        normalized = values[0]
    return _normalize_real(normalized, field_name="The affine intercept")


def _validate_feature_contract(
    *,
    model: SklearnAffineModel,
    feature_names: tuple[str, ...],
    coefficient_count: int,
) -> None:
    if len(feature_names) != coefficient_count:
        raise ValueError(
            "ModelSchema feature count does not match affine coefficients: "
            f"{len(feature_names)} != {coefficient_count}."
        )

    declared = getattr(model, "feature_names_in_", None)
    if declared is not None:
        normalized = _to_builtin(declared)
        if not _is_sequence(normalized):
            raise ValueError("sklearn feature_names_in_ must be a sequence.")
        source_names = tuple(str(value) for value in cast(Sequence[Any], normalized))
        if source_names != feature_names:
            raise ValueError(
                "ModelSchema feature order does not match sklearn "
                f"feature_names_in_: {feature_names!r} != {source_names!r}."
            )

    declared_count = getattr(model, "n_features_in_", None)
    if declared_count is not None and int(declared_count) != coefficient_count:
        raise ValueError(
            "sklearn n_features_in_ does not match affine coefficients: "
            f"{int(declared_count)} != {coefficient_count}."
        )


def _required_fitted_attribute(model: SklearnAffineModel, name: str) -> Any:
    try:
        return getattr(model, name)
    except AttributeError as error:
        raise ValueError(
            f"The sklearn affine model is not fitted: missing {name}."
        ) from error


def _to_builtin(value: Any) -> Any:
    tolist = getattr(value, "tolist", None)
    return tolist() if callable(tolist) else value


def _is_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes))


def _normalize_real(value: Any, *, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{field_name} must contain real numeric values.")
    return float(value)
