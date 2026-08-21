from __future__ import annotations

from toetra._models.ir.base import ModelIR
from toetra._models.ir_builder.defaults import create_default_model_ir_builder_registry
from toetra._models.ir_builder.errors import (
    InvalidModelIRParameterError,
    ModelIRBuilderError,
)
from toetra._models.ir_builder.metadata_affine import MetadataAffineModelIRBuilder
from toetra._models.ir_builder.registry import ModelIRBuilderRegistry
from toetra._models.schema.model_schema import ModelSchema


class ModelIRFactory:
    """Construct Model IR from a fitted model or legacy schema metadata."""

    def __init__(self, registry: ModelIRBuilderRegistry | None = None) -> None:
        self.registry = registry or create_default_model_ir_builder_registry()

    def build(self, model: object, schema: ModelSchema) -> ModelIR:
        builder = self.registry.require(schema.framework, schema.model_type)
        try:
            return builder.build(model, schema)
        except ModelIRBuilderError:
            raise
        except (TypeError, ValueError) as error:
            raise InvalidModelIRParameterError(str(error)) from error

    def build_from_schema(self, schema: ModelSchema) -> ModelIR:
        return MetadataAffineModelIRBuilder().build(schema)
