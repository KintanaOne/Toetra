from __future__ import annotations

from dsl.ir.ir1.nodes import ScopeIR
from dsl.ir.ir2.nodes import AssumptionIR2
from model.encoder.base import ModelEncoder, validate_model_assumptions
from model.encoder.context import ModelEncodingContext
from model.encoder.registry import ModelEncoderRegistry
from model.schema.model_schema import ModelSchema


class ModelEncoderFactory:
    """Select and execute a ModelEncoder for a ModelSchema."""

    def __init__(self, registry: ModelEncoderRegistry | None = None):
        self.registry = registry or ModelEncoderRegistry()

    def create(self, schema: ModelSchema) -> ModelEncoder:
        """Return the encoder matching a schema framework/model_type."""
        return self.registry.require(
            schema.framework,
            model_type=schema.model_type,
        )

    def encode(
        self,
        schema: ModelSchema,
        scope: ScopeIR,
        *,
        context: ModelEncodingContext | None = None,
    ) -> tuple[AssumptionIR2, ...]:
        """Encode model assumptions and validate the encoder boundary."""
        encoder = self.create(schema)
        assumptions = encoder.encode(schema, scope, context=context)
        return validate_model_assumptions(assumptions)
