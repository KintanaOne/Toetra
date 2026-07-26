from __future__ import annotations

from toetra._compiler.ir.ir1.nodes import AtomicIR
from toetra._compiler.ir.ir2.dsl.nodes import (
    AssumptionIR2,
    CNFFormulaIR2,
    DNFFormulaIR2,
    LiteralIR2,
    NNFFormulaIR2,
    VerificationTaskIR2,
)
from toetra._compiler.ir.ir2.enums import NormalFormKind, Polarity
from toetra._compiler.ir.ir2.errors import IR2ValidationError
from toetra._compiler.ir.ir2.guard import NNFGuard


class IR2Validator:
    """Validates VerificationTaskIR2 invariants."""

    def validate(self, task: VerificationTaskIR2) -> None:
        if not isinstance(task.spec_formula, NNFFormulaIR2):
            raise IR2ValidationError("spec_formula must be NNFFormulaIR2.")

        NNFGuard.assert_expr_is_nnf(task.spec_formula.expression)
        self._validate_assumptions(task.assumptions)

        if task.normal_form == NormalFormKind.NNF:
            if not isinstance(task.verification_condition, NNFFormulaIR2):
                raise IR2ValidationError("normal_form=NNF requires NNFFormulaIR2.")
            NNFGuard.assert_expr_is_nnf(task.verification_condition.expression)

        elif task.normal_form == NormalFormKind.CNF:
            if not isinstance(task.verification_condition, CNFFormulaIR2):
                raise IR2ValidationError("normal_form=CNF requires CNFFormulaIR2.")
            self._validate_cnf(task.verification_condition)

        elif task.normal_form == NormalFormKind.DNF:
            if not isinstance(task.verification_condition, DNFFormulaIR2):
                raise IR2ValidationError("normal_form=DNF requires DNFFormulaIR2.")
            self._validate_dnf(task.verification_condition)

        else:
            raise IR2ValidationError(f"Unsupported normal form: {task.normal_form}")

        if task.requirements.normal_form != task.normal_form:
            raise IR2ValidationError(
                "requirements.normal_form must match task.normal_form."
            )

        self._validate_point_aware_contract(task)

    def _validate_point_aware_contract(self, task: VerificationTaskIR2) -> None:
        source_names = [mapping.source_name for mapping in task.point_mappings]
        if len(source_names) != len(set(source_names)):
            raise IR2ValidationError(
                "point_mappings must contain unique source point names."
            )
        mapped_points = tuple(mapping.ir_point for mapping in task.point_mappings)
        if len(mapped_points) != len(set(mapped_points)):
            raise IR2ValidationError(
                "point_mappings must contain unique IR point identities."
            )
        if len(task.model_evaluations) != len(set(task.model_evaluations)):
            raise IR2ValidationError(
                "model_evaluations must be deduplicated by (model, point, target)."
            )
        mapped_point_set = set(mapped_points)
        for evaluation in task.model_evaluations:
            if mapped_point_set and evaluation.point not in mapped_point_set:
                raise IR2ValidationError(
                    "Every model evaluation point must be present in point_mappings."
                )
        requirements = task.requirements
        if requirements.point_count != len(task.point_mappings):
            raise IR2ValidationError(
                "requirements.point_count must match task.point_mappings."
            )
        if requirements.model_evaluation_count != len(task.model_evaluations):
            raise IR2ValidationError(
                "requirements.model_evaluation_count must match task.model_evaluations."
            )
        if requirements.binder_sequence != task.quantifier_structure.binder_sequence:
            raise IR2ValidationError(
                "requirements.binder_sequence must match quantifier_structure."
            )
        if (
            requirements.alternation_depth
            != task.quantifier_structure.alternation_depth
        ):
            raise IR2ValidationError(
                "requirements.alternation_depth must match quantifier_structure."
            )
        if (
            requirements.requires_quantifier_alternation
            != task.quantifier_structure.is_alternating
        ):
            raise IR2ValidationError(
                "Quantifier alternation requirement must match the binder sequence."
            )
        if (
            task.quantifier_structure.is_alternating
            and not requirements.requires_native_quantifiers
        ):
            raise IR2ValidationError(
                "Alternating quantifiers require native/advanced capability."
            )

    def _validate_assumptions(
        self,
        assumptions: tuple[AssumptionIR2, ...],
    ) -> None:
        for index, assumption in enumerate(assumptions):
            if not isinstance(assumption, AssumptionIR2):
                raise IR2ValidationError(
                    f"assumptions[{index}] must be AssumptionIR2, "
                    f"got {type(assumption).__name__}."
                )

            if not isinstance(assumption.formula, NNFFormulaIR2):
                raise IR2ValidationError(
                    f"assumptions[{index}].formula must be NNFFormulaIR2."
                )

            NNFGuard.assert_expr_is_nnf(assumption.formula.expression)

    def _validate_cnf(self, formula: CNFFormulaIR2) -> None:
        if not formula.clauses:
            raise IR2ValidationError("CNFFormulaIR2 must contain at least one clause.")

        for clause_index, clause in enumerate(formula.clauses):
            if not clause.literals:
                raise IR2ValidationError(
                    f"CNF clause at index {clause_index} must contain literals."
                )

            for literal_index, literal in enumerate(clause.literals):
                self._validate_literal(
                    literal,
                    location=f"CNF clause {clause_index}, literal {literal_index}",
                )

    def _validate_dnf(self, formula: DNFFormulaIR2) -> None:
        if not formula.terms:
            raise IR2ValidationError("DNFFormulaIR2 must contain at least one term.")

        for term_index, term in enumerate(formula.terms):
            if not term.literals:
                raise IR2ValidationError(
                    f"DNF term at index {term_index} must contain literals."
                )

            for literal_index, literal in enumerate(term.literals):
                self._validate_literal(
                    literal,
                    location=f"DNF term {term_index}, literal {literal_index}",
                )

    def _validate_literal(self, literal: LiteralIR2, *, location: str) -> None:
        if not isinstance(literal, LiteralIR2):
            raise IR2ValidationError(
                f"{location} must be LiteralIR2, got {type(literal).__name__}."
            )

        if not isinstance(literal.polarity, Polarity):
            raise IR2ValidationError(
                f"{location} has invalid polarity: {literal.polarity!r}."
            )

        if not isinstance(literal.atom, AtomicIR):
            raise IR2ValidationError(
                f"{location} atom must be AtomicIR, "
                f"got {type(literal.atom).__name__}."
            )
