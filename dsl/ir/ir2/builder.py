from __future__ import annotations

from dsl.ir.ir1.nodes import VerificationTask
from dsl.ir.ir2.assumptions import AssumptionCollector
from dsl.ir.ir2.condition import VerificationConditionBuilder
from dsl.ir.ir2.context import IR2BuildContext
from dsl.ir.ir2.enums import NormalFormKind, VerificationSemantics
from dsl.ir.ir2.errors import NormalFormExplosionError
from dsl.ir.ir2.guard import NNFGuard
from dsl.ir.ir2.nodes import (
    AssumptionIR2,
    FormulaIR2,
    NNFFormulaIR2,
    VerificationTaskIR2,
)
from dsl.ir.ir2.normal_forms.cnf import CNFConverter
from dsl.ir.ir2.normal_forms.dnf import DNFConverter
from dsl.ir.ir2.requirements import RequirementsAnalyzer
from dsl.ir.ir2.selector import NormalFormSelector
from dsl.ir.ir2.validator import IR2Validator


class IR2Builder:
    """Public IR2 construction entrypoint.

    This class orchestrates specialized components. It does not encode models,
    translate to a concrete backend, or own the normal-form algorithms.
    """

    def __init__(
        self,
        *,
        assumption_collector: AssumptionCollector | None = None,
        vc_builder: VerificationConditionBuilder | None = None,
        selector: NormalFormSelector | None = None,
        cnf_converter: CNFConverter | None = None,
        dnf_converter: DNFConverter | None = None,
        requirements_analyzer: RequirementsAnalyzer | None = None,
        validator: IR2Validator | None = None,
    ):
        self.assumption_collector = assumption_collector or AssumptionCollector()
        self.vc_builder = vc_builder or VerificationConditionBuilder()
        self.selector = selector or NormalFormSelector()
        self.cnf_converter = cnf_converter or CNFConverter()
        self.dnf_converter = dnf_converter or DNFConverter()
        self.requirements_analyzer = requirements_analyzer or RequirementsAnalyzer()
        self.validator = validator or IR2Validator()

    def build(
        self,
        task_nnf: VerificationTask,
        *,
        assumptions: tuple[AssumptionIR2, ...] | list[AssumptionIR2] | None = None,
        context: IR2BuildContext | None = None,
    ) -> VerificationTaskIR2:
        context = context or IR2BuildContext(backend_hint=task_nnf.backend)

        NNFGuard.assert_task_is_nnf(task_nnf)

        collected_assumptions = self.assumption_collector.collect(assumptions)
        spec_formula = NNFFormulaIR2(expression=task_nnf.query.expression)

        vc_nnf = self.vc_builder.build_refutation_condition(
            spec_formula=spec_formula,
            assumptions=collected_assumptions,
        )

        selected_form = self.selector.select(vc_nnf, context=context)
        verification_condition, actual_form = self._convert(vc_nnf, selected_form, context)

        requirements = self.requirements_analyzer.analyze(
            scope=task_nnf.scope,
            verification_condition=verification_condition,
            assumptions=collected_assumptions,
            normal_form=actual_form,
        )

        task_ir2 = VerificationTaskIR2(
            property_type=task_nnf.property_type,
            scope=task_nnf.scope,
            backend=task_nnf.backend,
            assumptions=collected_assumptions,
            spec_formula=spec_formula,
            verification_condition=verification_condition,
            semantics=VerificationSemantics.REFUTATION,
            normal_form=actual_form,
            requirements=requirements,
            metadata={
                "source_ir": "ir1_nnf",
                "builder": "IR2Builder",
            },
        )

        self.validator.validate(task_ir2)
        return task_ir2

    def build_tasks(
        self,
        tasks_nnf: list[VerificationTask],
        *,
        assumptions: tuple[AssumptionIR2, ...] | list[AssumptionIR2] | None = None,
        context: IR2BuildContext | None = None,
    ) -> list[VerificationTaskIR2]:
        return [self.build(task, assumptions=assumptions, context=context) for task in tasks_nnf]

    def _convert(
        self,
        vc_nnf: NNFFormulaIR2,
        selected_form: NormalFormKind,
        context: IR2BuildContext,
    ) -> tuple[FormulaIR2, NormalFormKind]:
        if selected_form == NormalFormKind.NNF:
            return vc_nnf, NormalFormKind.NNF

        try:
            if selected_form == NormalFormKind.CNF:
                return self.cnf_converter.convert(vc_nnf.expression, context=context), NormalFormKind.CNF

            if selected_form == NormalFormKind.DNF:
                return self.dnf_converter.convert(vc_nnf.expression, context=context), NormalFormKind.DNF

        except NormalFormExplosionError:
            if context.allow_nnf_fallback:
                return vc_nnf, NormalFormKind.NNF
            raise

        return vc_nnf, NormalFormKind.NNF
