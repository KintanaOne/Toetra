from __future__ import annotations

from toetra._compiler.ir.ir1.nodes import ModelEvaluationIR
from toetra._compiler.ir.ir2.nodes import AssumptionIR2
from toetra._models.encoder.base import (
    ModelEncoder,
    validate_model_assumptions,
    validate_model_evaluation_coverage,
)
from toetra._models.encoder.context import ModelEncodingContext
from toetra._models.encoder.defaults import create_default_model_encoder_registry
from toetra._models.encoder.registry import ModelEncoderRegistry
from toetra._models.schema.model_schema import ModelSchema


class ModelEncoderFactory:
    """Select and execute a ModelEncoder for a ModelSchema."""

    def __init__(self, registry: ModelEncoderRegistry | None = None):
        self.registry = registry or create_default_model_encoder_registry()

    def create(self, schema: ModelSchema) -> ModelEncoder:
        """Return the encoder matching a schema framework/model_type."""
        return self.registry.require(
            schema.framework,
            model_type=schema.model_type,
        )

    def encode(
        self,
        schema: ModelSchema,
        evaluations: tuple[ModelEvaluationIR, ...],
        *,
        context: ModelEncodingContext | None = None,
    ) -> tuple[AssumptionIR2, ...]:
        """Encode exactly the requested model evaluations.

        The factory deliberately receives structured evaluation identities
        rather than a scope. Input-point selection is owned by semantic/IR
        analysis and must never be guessed by the model encoder.
        """
        unique_evaluations = tuple(dict.fromkeys(evaluations))
        effective_context = context or ModelEncodingContext()
        encoder = self.create(schema)
        assumptions = validate_model_assumptions(
            encoder.encode(schema, unique_evaluations, context=effective_context)
        )
        if (
            effective_context.include_model_constraints
            and effective_context.include_output_constraints
        ):
            validate_model_evaluation_coverage(assumptions, unique_evaluations)
        return assumptions
