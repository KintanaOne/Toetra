from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from toetra._compiler.ir.ir1.run_ir1 import run_ir, run_ir_from_program
from toetra._compiler.ir.ir2.builder import IR2Builder
from toetra._compiler.ir.ir2.context import IR2BuildContext
from toetra._compiler.ir.ir2.dsl.nodes import (
    AssumptionIR2,
    NNFFormulaIR2,
    VerificationTaskIR2,
)
from toetra._compiler.ir.normalization.nnf import NNFNormalizer
from toetra._models.semantics.lowering import ModelSemanticLowerer

if TYPE_CHECKING:
    from toetra._compiler.ast.nodes.program import ProgramNode
    from toetra._compiler.model_lowering.factory import ModelIRLoweringFactory
    from toetra._models.encoder.context import ModelEncodingContext
    from toetra._models.encoder.factory import ModelEncoderFactory
    from toetra._models.ir.base import ModelIR
    from toetra._models.schema.model_schema import ModelSchema
    from toetra._compiler.semantic.symbols.point import ResolvedAnchorBinding


def run_ir2(
    source: str,
    *,
    assumptions: tuple[AssumptionIR2, ...] | list[AssumptionIR2] | None = None,
    context: IR2BuildContext | None = None,
) -> list[VerificationTaskIR2]:
    """Compile Toetra source to IR2.

    ``assumptions`` are applied to every generated task. This is useful for
    global assumptions. For model assumptions, prefer
    ``run_ir2_with_model_schema`` because model assumptions are evaluation-
    dependent.
    """

    ir1_tasks = run_ir(source)
    ModelSemanticLowerer.assert_no_unlowered_observables(ir1_tasks)
    nnf_tasks = NNFNormalizer().normalize_tasks(ir1_tasks)
    return IR2Builder().build_tasks(
        nnf_tasks,
        assumptions=assumptions,
        context=context,
        source_spec_formulas=tuple(task.query.expression for task in ir1_tasks),
    )


def run_ir2_with_model_schema(
    source: str,
    *,
    schema: ModelSchema,
    model_context: ModelEncodingContext | None = None,
    ir2_context: IR2BuildContext | None = None,
    encoder_factory: ModelEncoderFactory | None = None,
    model_ir: ModelIR | None = None,
    model_lowering_factory: ModelIRLoweringFactory | None = None,
    resolved_anchors: Mapping[str, ResolvedAnchorBinding] | None = None,
    program: ProgramNode | None = None,
) -> list[VerificationTaskIR2]:
    """Compile Toetra source to IR2 and inject per-evaluation model equations.

    The compiler first discovers the exact structured model evaluations
    referenced by each task. Compiler-owned Model IR lowering then emits one
    equation for each requested ``(model, point, target)`` identity and none
    for unreferenced points. An explicitly supplied ``encoder_factory`` keeps
    the legacy advanced-integration seam.
    """

    from toetra._compiler.model_lowering.factory import ModelIRLoweringFactory
    from toetra._models.ir_builder.factory import ModelIRFactory

    if encoder_factory is not None and (
        model_ir is not None or model_lowering_factory is not None
    ):
        raise ValueError(
            "Provide either a legacy encoder_factory or the Model IR lowering "
            "path, not both."
        )

    effective_model_ir = model_ir
    lowerer_factory = model_lowering_factory
    if encoder_factory is None:
        effective_model_ir = effective_model_ir or ModelIRFactory().build_from_schema(
            schema
        )
        lowerer_factory = lowerer_factory or ModelIRLoweringFactory()

    ir1_tasks = (
        run_ir(
            source,
            model_schema=schema,
            resolved_anchors=resolved_anchors,
        )
        if program is None
        else run_ir_from_program(
            program,
            model_schema=schema,
            resolved_anchors=resolved_anchors,
        )
    )
    lowerer = ModelSemanticLowerer()
    lowered_tasks = [lowerer.lower_task(task, schema=schema) for task in ir1_tasks]

    builder = IR2Builder()
    tasks: list[VerificationTaskIR2] = []

    for lowered in lowered_tasks:
        task = NNFNormalizer().normalize_task(lowered.task)
        spec_formula = NNFFormulaIR2(expression=task.query.expression)
        requested_evaluations = builder.point_analyzer.model_evaluations(
            spec_formula=spec_formula,
        )
        if encoder_factory is not None:
            model_assumptions = encoder_factory.encode(
                schema,
                requested_evaluations,
                context=model_context,
            )
        else:
            assert effective_model_ir is not None
            assert lowerer_factory is not None
            model_assumptions = lowerer_factory.lower(
                effective_model_ir,
                schema,
                requested_evaluations,
                context=model_context,
            )
        tasks.append(
            builder.build(
                task,
                assumptions=model_assumptions,
                context=ir2_context,
                lowering_evidence=lowered.evidence,
                source_spec_formula=ir1_tasks[len(tasks)].query.expression,
            )
        )

    return tasks
