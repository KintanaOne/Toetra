from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from toetra._compatibility.descriptors import FrameworkModelDescriptor
from toetra._compiler.semantic.types.enums import EnumDataType

from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.metadata import (
    FrozenMetadataMap,
    FrozenMetadataValue,
    MetadataEntry,
    freeze_metadata,
    thaw_metadata,
)
from toetra._models.schema.output_schema import (
    ClassificationOutputSchema,
    EnumModelOutputKind,
    ModelOutputSchema,
    RegressionOutputSchema,
    UnknownOutputSchema,
)


@dataclass(frozen=True, init=False, slots=True)
class ModelSchema:
    """Normalized Toetra model representation.

    ``output_name`` and ``output_schema`` are the source of truth for the
    selected output port. ``target`` and the ``target_*`` attributes remain
    read-only compatibility projections while Patch 21 migrates older callers.
    """

    framework: EnumModelFramework
    model_type: str
    features: tuple[FeatureSchema, ...]
    output_name: str
    task: str
    output_schema: ModelOutputSchema
    metadata: tuple[MetadataEntry, ...]
    compatibility: FrameworkModelDescriptor | None = None

    def __init__(
        self,
        framework: EnumModelFramework,
        model_type: str,
        features: Mapping[str, FeatureSchema] | Iterable[FeatureSchema],
        target: str | None = None,
        task: str = "unknown",
        target_dtype: EnumDataType | None = None,
        metadata: Mapping[str, Any] | tuple[MetadataEntry, ...] | None = None,
        compatibility: FrameworkModelDescriptor | None = None,
        target_source_dtype: str | None = None,
        *,
        output_name: str | None = None,
        output_schema: ModelOutputSchema | None = None,
    ) -> None:
        _validate_framework(framework)
        _validate_text(model_type, field_name="model_type")
        _validate_text(task, field_name="task")
        normalized_features = _normalize_features(features)
        normalized_metadata = freeze_metadata(metadata)
        resolved_output_name = _resolve_output_name(
            output_name=output_name,
            target=target,
        )
        resolved_output_schema = output_schema or _legacy_output_schema(
            task=task,
            target_dtype=target_dtype,
            target_source_dtype=target_source_dtype,
            metadata=FrozenMetadataMap(normalized_metadata),
        )
        if type(resolved_output_schema) not in (
            RegressionOutputSchema,
            ClassificationOutputSchema,
            UnknownOutputSchema,
        ):
            raise TypeError(
                "ModelSchema output_schema must be a supported immutable "
                "ModelOutputSchema value."
            )
        _validate_output_kind(task=task, output_schema=resolved_output_schema)
        _validate_compatibility_projection(
            output_schema=resolved_output_schema,
            target_dtype=target_dtype,
            target_source_dtype=target_source_dtype,
        )

        if compatibility is not None and not isinstance(
            compatibility, FrameworkModelDescriptor
        ):
            raise TypeError(
                "ModelSchema compatibility must be a FrameworkModelDescriptor "
                "or None."
            )

        object.__setattr__(self, "framework", framework)
        object.__setattr__(self, "model_type", model_type)
        object.__setattr__(self, "features", normalized_features)
        object.__setattr__(self, "output_name", resolved_output_name)
        object.__setattr__(self, "task", task)
        object.__setattr__(self, "output_schema", resolved_output_schema)
        object.__setattr__(self, "metadata", normalized_metadata)
        object.__setattr__(self, "compatibility", compatibility)

    @property
    def feature_names(self) -> tuple[str, ...]:
        """Return normalized input names in model order."""

        return tuple(feature.name for feature in self.features)

    @property
    def features_by_name(self) -> Mapping[str, FeatureSchema]:
        """Return a read-only feature lookup detached from caller-owned mappings."""

        return MappingProxyType({feature.name: feature for feature in self.features})

    def get_feature(self, name: str) -> FeatureSchema | None:
        """Return one normalized feature without exposing mutable lookup state."""

        return next(
            (feature for feature in self.features if feature.name == name), None
        )

    @property
    def metadata_by_name(self) -> FrozenMetadataMap:
        """Return metadata through an immutable mapping-compatible view."""

        return FrozenMetadataMap(self.metadata)

    def get_metadata(
        self,
        key: str,
        default: FrozenMetadataValue | None = None,
    ) -> FrozenMetadataValue | None:
        """Return one deeply immutable metadata value."""

        return self.metadata_by_name.get(key, default)

    def metadata_as_dict(self) -> dict[str, Any]:
        """Return detached built-ins suitable for serialization and reports."""

        return thaw_metadata(self.metadata)

    @property
    def output(self) -> ModelOutputSchema:
        """Return the typed output schema using concise output terminology."""

        return self.output_schema

    @property
    def target(self) -> str:
        """Compatibility projection for pre-Patch-21 callers."""

        return self.output_name

    @property
    def target_dtype(self) -> EnumDataType | None:
        """Compatibility projection of the output's primary public dtype."""

        return self.output_schema.primary_dtype

    @property
    def target_source_dtype(self) -> str | None:
        """Compatibility projection of the output's source dtype."""

        return self.output_schema.source_dtype


def _resolve_output_name(*, output_name: str | None, target: str | None) -> str:
    if output_name is not None:
        _validate_text(output_name, field_name="output_name")
    if target is not None:
        _validate_text(target, field_name="target")
    if output_name is not None and target is not None and output_name != target:
        raise ValueError(
            "ModelSchema output_name and compatibility target must identify "
            "the same output port"
        )

    resolved = output_name if output_name is not None else target
    if resolved is None or not resolved.strip():
        raise ValueError("ModelSchema requires a non-empty output name")
    return resolved


def _legacy_output_schema(
    *,
    task: str,
    target_dtype: EnumDataType | None,
    target_source_dtype: str | None,
    metadata: Mapping[str, Any],
) -> ModelOutputSchema:
    if task == "regression":
        return RegressionOutputSchema(
            value_dtype=target_dtype,
            value_source_dtype=target_source_dtype,
        )

    if task == "classification":
        labels = _normalize_legacy_labels(metadata.get("classes"))
        return ClassificationOutputSchema(
            label_dtype=target_dtype,
            labels=labels,
            label_source_dtype=target_source_dtype,
            probability_available=False,
        )

    return UnknownOutputSchema(
        value_dtype=target_dtype,
        value_source_dtype=target_source_dtype,
    )


def _normalize_legacy_labels(value: Any) -> tuple[str | int | float | bool, ...]:
    if value is None:
        return ()
    if hasattr(value, "tolist"):
        value = value.tolist()
    if not isinstance(value, (list, tuple)):
        value = [value]

    normalized: list[str | int | float | bool] = []
    for label in value:
        if hasattr(label, "item"):
            label = label.item()
        if not isinstance(label, (str, int, float, bool)):
            raise TypeError(
                "Classification labels must normalize to string, integer, "
                "float, or boolean values"
            )
        normalized.append(label)
    return tuple(normalized)


def _validate_output_kind(*, task: str, output_schema: ModelOutputSchema) -> None:
    expected = {
        "regression": EnumModelOutputKind.REGRESSION,
        "classification": EnumModelOutputKind.CLASSIFICATION,
        "unknown": EnumModelOutputKind.UNKNOWN,
    }.get(task)
    if expected is not None and output_schema.kind is not expected:
        raise ValueError(
            "ModelSchema task conflicts with the typed output schema kind: "
            f"{task!r} != {output_schema.kind.value!r}"
        )


def _validate_compatibility_projection(
    *,
    output_schema: ModelOutputSchema,
    target_dtype: EnumDataType | None,
    target_source_dtype: str | None,
) -> None:
    if target_dtype is not None and output_schema.primary_dtype != target_dtype:
        raise ValueError(
            "ModelSchema target_dtype compatibility projection conflicts with "
            "the typed output schema"
        )
    if (
        target_source_dtype is not None
        and output_schema.source_dtype != target_source_dtype
    ):
        raise ValueError(
            "ModelSchema target_source_dtype compatibility projection conflicts "
            "with the typed output schema"
        )


def _normalize_features(
    features: Mapping[str, FeatureSchema] | Iterable[FeatureSchema],
) -> tuple[FeatureSchema, ...]:
    if isinstance(features, Mapping):
        normalized = tuple(features.values())
        for key, feature in features.items():
            if not isinstance(key, str):
                raise TypeError("ModelSchema feature mapping keys must be strings.")
            if not isinstance(feature, FeatureSchema):
                raise TypeError("ModelSchema features must be FeatureSchema values.")
            if key != feature.name:
                raise ValueError(
                    "ModelSchema feature mapping keys must match FeatureSchema names: "
                    f"{key!r} != {feature.name!r}."
                )
    else:
        normalized = tuple(features)

    seen: set[str] = set()
    for feature in normalized:
        if not isinstance(feature, FeatureSchema):
            raise TypeError("ModelSchema features must be FeatureSchema values.")
        if feature.name in seen:
            raise ValueError(f"Duplicate ModelSchema feature name: {feature.name!r}.")
        seen.add(feature.name)
    return normalized


def _validate_framework(framework: object) -> None:
    if not isinstance(framework, EnumModelFramework):
        raise TypeError("ModelSchema framework must be an EnumModelFramework.")


def _validate_text(value: object, *, field_name: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"ModelSchema {field_name} must be a string.")
    if not value:
        raise ValueError(f"ModelSchema {field_name} cannot be empty.")
    if value.strip() != value:
        raise ValueError(
            f"ModelSchema {field_name} cannot have leading or trailing whitespace."
        )
    if field_name == "task" and value not in {
        "regression",
        "classification",
        "unknown",
    }:
        raise ValueError(
            "ModelSchema task must be 'regression', 'classification', or 'unknown'."
        )
