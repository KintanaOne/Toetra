from __future__ import annotations

from typing import TYPE_CHECKING

from dsl.ir.ir1.run_ir1 import run_ir
from dsl.ir.ir2.builder import IR2Builder
from dsl.ir.ir2.context import IR2BuildContext
from dsl.ir.ir2.nodes import AssumptionIR2, VerificationTaskIR2
from dsl.ir.normalization.nnf import NNFNormalizer

if TYPE_CHECKING:
    from model.encoder.context import ModelEncodingContext
    from model.encoder.factory import ModelEncoderFactory
    from model.schema.model_schema import ModelSchema


def run_ir2(
    source: str,
    *,
    assumptions: tuple[AssumptionIR2, ...] | list[AssumptionIR2] | None = None,
    context: IR2BuildContext | None = None,
) -> list[VerificationTaskIR2]:
    """Compile FORML source to IR2.

    ``assumptions`` are applied to every generated task. This is useful for
    global assumptions. For model assumptions, prefer
    ``run_ir2_with_model_schema`` because model assumptions are scope-dependent.
    """

    ir1_tasks = run_ir(source)
    nnf_tasks = NNFNormalizer().normalize_tasks(ir1_tasks)
    return IR2Builder().build_tasks(
        nnf_tasks,
        assumptions=assumptions,
        context=context,
    )


def run_ir2_with_model_schema(
    source: str,
    *,
    schema: ModelSchema,
    model_context: ModelEncodingContext | None = None,
    ir2_context: IR2BuildContext | None = None,
    encoder_factory: ModelEncoderFactory | None = None,
) -> list[VerificationTaskIR2]:
    """Compile FORML source to IR2 and inject model-derived assumptions.

    The model encoder is executed per task because the selected input entity
    depends on the task scope:
    - ``at x`` usually emits assumptions over ``x'``;
    - ``check_at x0`` emits assumptions over ``x0``;
    - ``forall`` emits assumptions over ``_x``.

    The resulting verification condition is still built by IR2 as ``Γ ∧ ¬P``.
    """

    from model.encoder.factory import ModelEncoderFactory

    ir1_tasks = run_ir(source)
    nnf_tasks = NNFNormalizer().normalize_tasks(ir1_tasks)

    builder = IR2Builder()
    factory = encoder_factory or ModelEncoderFactory()

    tasks: list[VerificationTaskIR2] = []

    for task in nnf_tasks:
        model_assumptions = factory.encode(
            schema,
            task.scope,
            context=model_context,
        )
        tasks.append(
            builder.build(
                task,
                assumptions=model_assumptions,
                context=ir2_context,
            )
        )

    return tasks
