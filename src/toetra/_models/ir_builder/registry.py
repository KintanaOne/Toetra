from __future__ import annotations

from dataclasses import dataclass, field

from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.ir_builder.base import ModelIRBuilder
from toetra._models.ir_builder.errors import UnsupportedModelIRBuilderError


@dataclass(frozen=True, slots=True)
class ModelIRBuilderKey:
    framework: EnumModelFramework
    model_type: str


@dataclass
class ModelIRBuilderRegistry:
    """Registry for framework-specific Model IR construction."""

    _builders: dict[ModelIRBuilderKey, ModelIRBuilder] = field(default_factory=dict)

    def register(
        self,
        framework: EnumModelFramework,
        model_type: str,
        builder: ModelIRBuilder,
    ) -> None:
        self._builders[ModelIRBuilderKey(framework, model_type)] = builder

    def require(
        self,
        framework: EnumModelFramework,
        model_type: str,
    ) -> ModelIRBuilder:
        builder = self._builders.get(ModelIRBuilderKey(framework, model_type))
        if builder is None:
            raise UnsupportedModelIRBuilderError(
                "No Model IR builder registered for "
                f"framework={framework.value}, model_type={model_type}."
            )
        return builder
