from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dsl.compatibility.descriptors import FrameworkModelDescriptor
from dsl.semantic.types.enums import EnumDataType

from model.detector.model_framework import EnumModelFramework
from model.schema.feature_schema import FeatureSchema
from model.schema.output_schema import (
    ClassificationOutputSchema,
    EnumModelOutputKind,
    ModelOutputSchema,
    RegressionOutputSchema,
    UnknownOutputSchema,
)


@dataclass(init=False)
class ModelSchema:
    """Normalized FORML model representation.

    ``output_name`` and ``output_schema`` are the source of truth for the
    selected output port. ``target`` and the ``target_*`` attributes remain
    read-only compatibility projections while Patch 21 migrates older callers.
    """

    framework: EnumModelFramework
    model_type: str
    features: dict[str, FeatureSchema]
    output_name: str
    task: str
    output_schema: ModelOutputSchema
    metadata: dict[str, Any] = field(default_factory=dict)
    compatibility: FrameworkModelDescriptor | None = None

    def __init__(
        self,
        framework: EnumModelFramework,
        model_type: str,
        features: dict[str, FeatureSchema],
        target: str | None = None,
        task: str = "unknown",
        target_dtype: EnumDataType | None = None,
        metadata: dict[str, Any] | None = None,
        compatibility: FrameworkModelDescriptor | None = None,
        target_source_dtype: str | None = None,
        *,
        output_name: str | None = None,
        output_schema: ModelOutputSchema | None = None,
    ) -> None:
        resolved_output_name = _resolve_output_name(
            output_name=output_name,
            target=target,
        )
        resolved_output_schema = output_schema or _legacy_output_schema(
            task=task,
            target_dtype=target_dtype,
            target_source_dtype=target_source_dtype,
            metadata=metadata or {},
        )
        _validate_output_kind(task=task, output_schema=resolved_output_schema)
        _validate_compatibility_projection(
            output_schema=resolved_output_schema,
            target_dtype=target_dtype,
            target_source_dtype=target_source_dtype,
        )

        self.framework = framework
        self.model_type = model_type
        self.features = features
        self.output_name = resolved_output_name
        self.task = task
        self.output_schema = resolved_output_schema
        self.metadata = dict(metadata or {})
        self.compatibility = compatibility

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
    metadata: dict[str, Any],
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
