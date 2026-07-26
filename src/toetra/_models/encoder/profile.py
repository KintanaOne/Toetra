from __future__ import annotations

from toetra._compatibility.descriptors import ModelEncoderDescriptor
from toetra._models.encoder.base import ModelEncoder


def model_encoder_descriptor(encoder: ModelEncoder) -> ModelEncoderDescriptor:
    """Return an encoder-declared profile or a conservative unknown fallback."""

    descriptor = getattr(encoder, "compatibility", None)
    if isinstance(descriptor, ModelEncoderDescriptor):
        return descriptor

    encoder_type = type(encoder)
    return ModelEncoderDescriptor(
        encoder_id=f"unknown:{encoder_type.__module__}.{encoder_type.__qualname__}",
        version="unknown",
        semantic_target="unknown",
    )
