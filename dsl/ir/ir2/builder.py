from __future__ import annotations

from dataclasses import replace

from dsl.ir.ir1.nodes import VerificationTask
from dsl.ir.ir2.assumptions import AssumptionCollector
from dsl.ir.ir2.condition import VerificationConditionBuilder
from dsl.ir.ir2.context import IR2BuildContext
from dsl.ir.ir2.domain_assumptions import DomainAssumptionEncoder
from dsl.ir.ir2.enums import NormalFormKind, VerificationSemantics
from dsl.ir.ir2.errors import NormalFormExplosionError
from dsl.ir.ir2.guard import NNFGuard
from dsl.ir.ir2.guardrails.validator import collect_ir2_diagnostics
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
        domain_assumption_encoder: DomainAssumptionEncoder | None = None,
        validator: IR2Validator | None = None,
    ):
        self.assumption_collector = assumption_collector or AssumptionCollector()
        self.vc_builder = vc_builder or VerificationConditionBuilder()
        self.selector = selector or NormalFormSelector()
        self.cnf_converter = cnf_converter or CNFConverter()
        self.dnf_converter = dnf_converter or DNFConverter()
        self.requirements_analyzer = requirements_analyzer or RequirementsAnalyzer()
        self.domain_assumption_encoder = (
            domain_assumption_encoder or DomainAssumptionEncoder()
        )
        self.validator = validator or IR2Validator()

    def build(
        self,
        task_nnf: VerificationTask,
        *,
        assumptions: tuple[AssumptionIR2, ...] | list[AssumptionIR2] | None = None,
        context: IR2BuildContext | None = None,
    ) -> VerificationTaskIR2:
        context = context or IR2BuildContext(
            backend_hint=task_nnf.backend,
        )

        NNFGuard.assert_task_is_nnf(task_nnf)

        domain_assumptions = self.domain_assumption_encoder.encode_domain(
            task_nnf.scope.domain
        )
        combined_assumptions = (
            *domain_assumptions,
            *(assumptions or ()),
        )
        collected_assumptions = self.assumption_collector.collect(
            combined_assumptions,
        )

        spec_formula = NNFFormulaIR2(
            expression=task_nnf.query.expression,
        )

        semantics = self._resolve_verification_semantics(
            task_nnf,
        )

        vc_nnf = self.vc_builder.build_condition(
            spec_formula=spec_formula,
            assumptions=collected_assumptions,
            semantics=semantics,
        )

        selected_form = self.selector.select(
            vc_nnf,
            context=context,
        )

        verification_condition, actual_form = self._convert(
            vc_nnf,
            selected_form,
            context,
        )

        requirements = self.requirements_analyzer.analyze(
            scope=task_nnf.scope,
            verification_condition=verification_condition,
            assumptions=collected_assumptions,
            normal_form=actual_form,
            semantics=semantics,
            # The current quantified scopes are eliminated into either:
            #
            #   Gamma AND NOT P
            #   Gamma AND P
            #
            # No native ForAll/Exists reaches the backend.
            requires_native_quantifiers=False,
        )

        task_ir2 = VerificationTaskIR2(
            property_type=task_nnf.property_type,
            scope=task_nnf.scope,
            backend=task_nnf.backend,
            assumptions=collected_assumptions,
            spec_formula=spec_formula,
            verification_condition=verification_condition,
            semantics=semantics,
            normal_form=actual_form,
            requirements=requirements,
            metadata={
                "source_ir": "ir1_nnf",
                "builder": "IR2Builder",
                "verification_semantics": semantics.value,
                "domain_assumption_count": len(domain_assumptions),
            },
        )

        self.validator.validate(task_ir2)

        diagnostics = collect_ir2_diagnostics(task_ir2)

        return replace(
            task_ir2,
            diagnostics=diagnostics,
        )

    @staticmethod
    def _resolve_verification_semantics(
        task: VerificationTask,
    ) -> VerificationSemantics:
        """Select verification semantics from the preserved IR1 scope.

        Non-quantified scopes and universal scopes use refutation:

            Gamma AND NOT P

        Existential scopes use satisfaction:

            Gamma AND P
        """

        scope = task.scope

        if scope.kind != "quantifier":
            return VerificationSemantics.REFUTATION

        quantifier = scope.quantifier

        if quantifier is None:
            raise ValueError("Quantified IR1 scope is missing its quantifier.")

        normalized = {
            "∀": "forall",
            "∃": "exists",
        }.get(
            quantifier.strip(),
            quantifier.strip().lower(),
        )

        if normalized == "forall":
            return VerificationSemantics.REFUTATION

        if normalized == "exists":
            return VerificationSemantics.SATISFACTION

        raise ValueError(f"Unsupported IR1 quantifier: {quantifier!r}")

    def build_tasks(
        self,
        tasks_nnf: list[VerificationTask],
        *,
        assumptions: tuple[AssumptionIR2, ...] | list[AssumptionIR2] | None = None,
        context: IR2BuildContext | None = None,
    ) -> list[VerificationTaskIR2]:
        return [
            self.build(
                task,
                assumptions=assumptions,
                context=context,
            )
            for task in tasks_nnf
        ]

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
                return (
                    self.cnf_converter.convert(
                        vc_nnf.expression,
                        context=context,
                    ),
                    NormalFormKind.CNF,
                )

            if selected_form == NormalFormKind.DNF:
                return (
                    self.dnf_converter.convert(
                        vc_nnf.expression,
                        context=context,
                    ),
                    NormalFormKind.DNF,
                )

        except NormalFormExplosionError:
            if context.allow_nnf_fallback:
                return vc_nnf, NormalFormKind.NNF

            raise

        return vc_nnf, NormalFormKind.NNF
