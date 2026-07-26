from __future__ import annotations

from dataclasses import dataclass, field

from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.encoder.base import ModelEncoder
from toetra._models.encoder.errors import UnsupportedModelEncoderError


@dataclass(frozen=True)
class ModelEncoderKey:
    """Registry key for model encoders.

    model_type=None means framework-level fallback.
    """

    framework: EnumModelFramework
    model_type: str | None = None


@dataclass(frozen=True)
class ModelEncoderRegistration:
    key: ModelEncoderKey
    encoder: ModelEncoder


@dataclass
class ModelEncoderRegistry:
    """Registry of backend-independent model encoders.

    Resolution order:
    1. exact match: framework + model_type
    2. fallback match: framework + None
    """

    _encoders: dict[ModelEncoderKey, ModelEncoder] = field(default_factory=dict)

    def register(
        self,
        framework: EnumModelFramework,
        encoder: ModelEncoder,
        *,
        model_type: str | None = None,
    ) -> None:
        self._encoders[ModelEncoderKey(framework, model_type)] = encoder

    def get(
        self,
        framework: EnumModelFramework,
        *,
        model_type: str | None = None,
    ) -> ModelEncoder | None:
        exact = self._encoders.get(ModelEncoderKey(framework, model_type))
        if exact is not None:
            return exact

        return self._encoders.get(ModelEncoderKey(framework, None))

    def require(
        self,
        framework: EnumModelFramework,
        *,
        model_type: str | None = None,
    ) -> ModelEncoder:
        encoder = self.get(framework, model_type=model_type)
        if encoder is None:
            model_label = model_type if model_type is not None else "<any>"
            raise UnsupportedModelEncoderError(
                f"No model encoder registered for "
                f"framework={framework.value}, model_type={model_label}."
            )
        return encoder

    def all(self) -> tuple[ModelEncoderRegistration, ...]:
        return tuple(
            ModelEncoderRegistration(key=key, encoder=encoder)
            for key, encoder in self._encoders.items()
        )

    def clear(self) -> None:
        self._encoders.clear()
