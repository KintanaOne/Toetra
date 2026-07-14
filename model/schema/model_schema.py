from dataclasses import dataclass, field
from typing import Any

from model.detector.model_framework import EnumModelFramework
from dsl.semantic.types.enums import EnumDataType
from model.schema.feature_schema import FeatureSchema


@dataclass
class ModelSchema:
    """Normalized FORML model representation.
    This schema acts as the semantic bridge between:
        - ML frameworks
        - DSL semantic validation
        - backend lowering
    """

    # ======================================================
    # Core model identity
    # ======================================================

    framework: EnumModelFramework
    model_type: str

    # ======================================================
    # Dataset Schema
    # ======================================================

    features: dict[str, FeatureSchema]
    target: str

    # ======================================================
    # ML task metadata
    # ======================================================

    task: str
    target_dtype: EnumDataType | None = None

    # ======================================================
    # Optional framework-specific metadata
    # ======================================================

    metadata: dict[str, Any] = field(default_factory=dict)
