from __future__ import annotations

from typing import Protocol

from toetra._compiler.ir.ir1.nodes import ModelEvaluationIR
from toetra._compiler.ir.ir2.dsl.nodes import AssumptionIR2
from toetra._compiler.model_lowering.context import ModelLoweringContext
from toetra._models.ir.base import ModelIR
from toetra._models.schema.model_schema import ModelSchema


class ModelIRLowerer(Protocol):
    """Lower reusable model computation into evaluation-specific IR2."""

    def lower(
        self,
        model_ir: ModelIR,
        schema: ModelSchema,
        evaluations: tuple[ModelEvaluationIR, ...],
        *,
        context: ModelLoweringContext | None = None,
    ) -> tuple[AssumptionIR2, ...]: ...
