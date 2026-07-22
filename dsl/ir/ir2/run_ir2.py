from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from dsl.ir.ir1.run_ir1 import run_ir
from dsl.ir.ir2.builder import IR2Builder
from dsl.ir.ir2.context import IR2BuildContext
from dsl.ir.ir2.nodes import AssumptionIR2, NNFFormulaIR2, VerificationTaskIR2
from dsl.ir.normalization.nnf import NNFNormalizer
from model.semantics.lowering import ModelSemanticLowerer

if TYPE_CHECKING:
    from model.encoder.context import ModelEncodingContext
    from model.encoder.factory import ModelEncoderFactory
    from model.schema.model_schema import ModelSchema
    from dsl.semantic.symbols.point import ResolvedAnchorBinding


def run_ir2(
    source: str,
    *,
    assumptions: tuple[AssumptionIR2, ...] | list[AssumptionIR2] | None = None,
    context: IR2BuildContext | None = None,
) -> list[VerificationTaskIR2]:
    """Compile FORML source to IR2.

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
    resolved_anchors: Mapping[str, ResolvedAnchorBinding] | None = None,
) -> list[VerificationTaskIR2]:
    """Compile FORML source to IR2 and inject per-evaluation model equations.

    The compiler first discovers the exact structured model evaluations
    referenced by each task. ModelBridge then emits one equation for each
    requested ``(model, point, target)`` identity and none for unreferenced
    points. The model encoder never inspects a scope to guess an input entity.
    """

    from model.encoder.factory import ModelEncoderFactory

    ir1_tasks = run_ir(
        source,
        model_schema=schema,
        resolved_anchors=resolved_anchors,
    )
    lowerer = ModelSemanticLowerer()
    lowered_tasks = [lowerer.lower_task(task, schema=schema) for task in ir1_tasks]

    builder = IR2Builder()
    factory = encoder_factory or ModelEncoderFactory()

    tasks: list[VerificationTaskIR2] = []

    for lowered in lowered_tasks:
        task = NNFNormalizer().normalize_task(lowered.task)
        spec_formula = NNFFormulaIR2(expression=task.query.expression)
        requested_evaluations = builder.point_analyzer.model_evaluations(
            spec_formula=spec_formula,
        )
        model_assumptions = factory.encode(
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
