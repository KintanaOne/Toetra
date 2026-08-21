from __future__ import annotations

from toetra._compatibility.descriptors import ModelEncoderDescriptor
from toetra._compiler.ir.ir1.nodes import ModelEvaluationIR
from toetra._compiler.ir.ir2.dsl.nodes import AssumptionIR2
from toetra._compiler.model_lowering.affine import AffineModelIRLowerer
from toetra._compiler.model_lowering.base import ModelIRLowerer
from toetra._compiler.model_lowering.context import ModelLoweringContext
from toetra._compiler.model_lowering.errors import UnsupportedModelIRLoweringError
from toetra._compiler.model_lowering.validation import (
    validate_lowered_model_assumptions,
)
from toetra._models.ir.affine import AffineModelIR
from toetra._models.ir.base import ModelIR
from toetra._models.schema.model_schema import ModelSchema


class ModelIRLoweringFactory:
    """Select and execute compiler lowering for one Model IR family."""

    def create(self, model_ir: ModelIR) -> ModelIRLowerer:
        if type(model_ir) is AffineModelIR:
            return AffineModelIRLowerer()
        raise UnsupportedModelIRLoweringError(
            f"No compiler lowerer registered for {type(model_ir).__name__}."
        )

    def descriptor(
        self,
        model_ir: ModelIR,
        schema: ModelSchema,
    ) -> ModelEncoderDescriptor:
        lowerer = self.create(model_ir)
        descriptor = getattr(lowerer, "descriptor", None)
        if not callable(descriptor):
            raise UnsupportedModelIRLoweringError(
                "Selected Model IR lowerer has no compatibility descriptor."
            )
        result = descriptor(schema)
        if not isinstance(result, ModelEncoderDescriptor):
            raise UnsupportedModelIRLoweringError(
                "Selected Model IR lowerer returned an invalid descriptor."
            )
        return result

    def lower(
        self,
        model_ir: ModelIR,
        schema: ModelSchema,
        evaluations: tuple[ModelEvaluationIR, ...],
        *,
        context: ModelLoweringContext | None = None,
    ) -> tuple[AssumptionIR2, ...]:
        effective_context = context or ModelLoweringContext()
        unique_evaluations = tuple(dict.fromkeys(evaluations))
        assumptions = self.create(model_ir).lower(
            model_ir,
            schema,
            unique_evaluations,
            context=effective_context,
        )
        if (
            not effective_context.include_model_constraints
            or not effective_context.include_output_constraints
        ):
            return tuple(assumptions)
        return validate_lowered_model_assumptions(assumptions, unique_evaluations)
