from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from toetra._compiler.ir.ir1.nodes import VerificationTask
from toetra._compiler.ir.ir2.anchor_assumptions import AnchorAssumptionEncoder
from toetra._compiler.ir.ir2.assumptions import AssumptionCollector
from toetra._compiler.ir.ir2.condition import VerificationConditionBuilder
from toetra._compiler.ir.ir2.context import IR2BuildContext
from toetra._compiler.ir.ir2.domain_assumptions import DomainAssumptionEncoder
from toetra._compiler.ir.ir2.enums import NormalFormKind, VerificationSemantics
from toetra._compiler.ir.ir2.errors import NormalFormExplosionError
from toetra._compiler.ir.ir2.guard import NNFGuard
from toetra._compiler.ir.ir2.guardrails.validator import collect_ir2_diagnostics
from toetra._compiler.ir.ir2.dsl.nodes import (
    AssumptionIR2,
    FormulaIR2,
    NNFFormulaIR2,
    VerificationTaskIR2,
)
from toetra._compiler.ir.ir2.normal_forms.cnf import CNFConverter
from toetra._compiler.ir.ir2.normal_forms.dnf import DNFConverter
from toetra._compiler.ir.ir2.points import PointAwareIR2Analyzer
from toetra._compiler.ir.ir2.requirements import RequirementsAnalyzer
from toetra._compiler.ir.ir2.selector import NormalFormSelector
from toetra._compiler.ir.ir2.validator import IR2Validator

if TYPE_CHECKING:
    from toetra._compiler.ir.ir1.nodes import LogicalIR
    from toetra._models.semantics.evidence import SemanticLoweringEvidence


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
        anchor_assumption_encoder: AnchorAssumptionEncoder | None = None,
        point_analyzer: PointAwareIR2Analyzer | None = None,
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
        self.anchor_assumption_encoder = (
            anchor_assumption_encoder or AnchorAssumptionEncoder()
        )
        self.point_analyzer = point_analyzer or PointAwareIR2Analyzer()
        self.validator = validator or IR2Validator()

    def build(
        self,
        task_nnf: VerificationTask,
        *,
        assumptions: tuple[AssumptionIR2, ...] | list[AssumptionIR2] | None = None,
        context: IR2BuildContext | None = None,
        lowering_evidence: tuple[SemanticLoweringEvidence, ...] = (),
        source_spec_formula: LogicalIR | None = None,
    ) -> VerificationTaskIR2:
        context = context or IR2BuildContext(
            backend_hint=task_nnf.backend,
        )

        NNFGuard.assert_task_is_nnf(task_nnf)

        anchor_assumptions = self.anchor_assumption_encoder.encode_scope(task_nnf.scope)
        domain_assumptions = self.domain_assumption_encoder.encode_domain(
            task_nnf.scope.domain
        )
        combined_assumptions = (
            *anchor_assumptions,
            *domain_assumptions,
            *(assumptions or ()),
        )
        collected_assumptions = self.assumption_collector.collect(
            combined_assumptions,
        )

        spec_formula = NNFFormulaIR2(
            expression=task_nnf.query.expression,
        )

        point_mappings = self.point_analyzer.point_mappings(task_nnf.scope)
        quantifier_structure = self.point_analyzer.quantifier_structure(task_nnf.scope)

        semantics = self._resolve_verification_semantics(
            task_nnf,
            quantifier_structure=quantifier_structure,
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

        model_evaluations = self.point_analyzer.model_evaluations(
            spec_formula=spec_formula,
        )

        requires_native_quantifiers = quantifier_structure.is_alternating

        requirements = self.requirements_analyzer.analyze(
            scope=task_nnf.scope,
            verification_condition=verification_condition,
            assumptions=collected_assumptions,
            normal_form=actual_form,
            semantics=semantics,
            requires_native_quantifiers=requires_native_quantifiers,
            point_mappings=point_mappings,
            model_evaluations=model_evaluations,
            quantifier_structure=quantifier_structure,
        )
        probability_lowerings = tuple(
            evidence
            for evidence in lowering_evidence
            if evidence.source_intent.observable.value == "class_probability"
        )
        if probability_lowerings:
            requirements = replace(
                requirements,
                requires_logistic_probability_threshold=True,
                requires_transcendental_threshold_lowering=any(
                    evidence.compatibility_classification.value != "exact"
                    for evidence in probability_lowerings
                ),
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
            point_mappings=point_mappings,
            model_evaluations=model_evaluations,
            quantifier_structure=quantifier_structure,
            source_spec_formula=source_spec_formula,
            metadata={
                "source_ir": "ir1_nnf",
                "builder": "IR2Builder",
                "verification_semantics": semantics.value,
                "anchor_assumption_count": len(anchor_assumptions),
                "domain_assumption_count": len(domain_assumptions),
                "point_count": len(point_mappings),
                "model_evaluation_count": len(model_evaluations),
                "binder_sequence": quantifier_structure.binder_sequence,
                "alternation_depth": quantifier_structure.alternation_depth,
            },
        )

        self.validator.validate(task_ir2)

        diagnostics = collect_ir2_diagnostics(task_ir2)

        return replace(
            task_ir2,
            diagnostics=diagnostics,
            lowering_evidence=lowering_evidence,
        )

    @staticmethod
    def _resolve_verification_semantics(
        task: VerificationTask,
        *,
        quantifier_structure,
    ) -> VerificationSemantics:
        """Select the outer goal without flattening the binder sequence."""
        outermost = quantifier_structure.outermost_quantifier
        if outermost is None:
            if task.scope.kind != "quantifier":
                return VerificationSemantics.REFUTATION
            raise ValueError("Quantified IR1 scope is missing its quantifier.")
        if outermost == "forall":
            return VerificationSemantics.REFUTATION
        if outermost == "exists":
            return VerificationSemantics.SATISFACTION
        raise ValueError(f"Unsupported IR1 quantifier: {outermost!r}")

    def build_tasks(
        self,
        tasks_nnf: list[VerificationTask],
        *,
        assumptions: tuple[AssumptionIR2, ...] | list[AssumptionIR2] | None = None,
        context: IR2BuildContext | None = None,
        lowering_evidence: tuple[SemanticLoweringEvidence, ...] = (),
        source_spec_formulas: tuple[LogicalIR | None, ...] | None = None,
    ) -> list[VerificationTaskIR2]:
        formulas = source_spec_formulas or tuple(None for _ in tasks_nnf)
        if len(formulas) != len(tasks_nnf):
            raise ValueError("source_spec_formulas must align with tasks_nnf")
        return [
            self.build(
                task,
                assumptions=assumptions,
                context=context,
                lowering_evidence=lowering_evidence,
                source_spec_formula=source_formula,
            )
            for task, source_formula in zip(tasks_nnf, formulas, strict=True)
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
