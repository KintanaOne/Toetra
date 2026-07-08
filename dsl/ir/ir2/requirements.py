from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from dsl.ir.ir1.nodes import (
    AndIR,
    AtomicIR,
    ComparisonIR,
    LogicalIR,
    NotIR,
    OrIR,
    ProblemIR,
    ScopeIR,
)
from dsl.ir.ir2.dsl.nodes import (
    AssumptionIR2,
    CNFFormulaIR2,
    DNFFormulaIR2,
    FormulaIR2,
    LiteralIR2,
    NNFFormulaIR2,
)
from dsl.ir.ir2.enums import AssumptionSource, NormalFormKind
from dsl.ir.ir2.model.affine import AffineOutputConstraintIR2
from dsl.ir.ir2.model.base import ModelConstraintIR2


@dataclass(frozen=True)
class IR2Requirements:
    """Backend-neutral capabilities required by a VerificationTaskIR2."""

    requires_boolean_logic: bool
    requires_numeric_comparisons: bool
    requires_problem_predicates: bool
    requires_model_assertions: bool
    requires_quantifiers: bool
    requires_domains: bool
    requires_neighborhoods: bool
    normal_form: NormalFormKind


class RequirementsAnalyzer:
    """Computes IR2 requirements for future backend routing."""

    def analyze(
        self,
        *,
        scope: ScopeIR,
        verification_condition: FormulaIR2,
        assumptions: tuple[AssumptionIR2, ...],
        normal_form: NormalFormKind,
    ) -> IR2Requirements:
        literals = list(self._iter_literals_or_atoms(verification_condition))
        assumption_literals = []
        for assumption in assumptions:
            assumption_literals.extend(self._iter_literals_or_atoms(assumption.formula))

        all_items = literals + assumption_literals

        return IR2Requirements(
            requires_boolean_logic=True,
            requires_numeric_comparisons=any(
                isinstance(item, (ComparisonIR, AffineOutputConstraintIR2))
                for item in all_items
            ),
            requires_problem_predicates=any(
                isinstance(item, ProblemIR) for item in all_items
            ),
            requires_model_assertions=any(
                a.source == AssumptionSource.MODEL for a in assumptions
            )
            or any(isinstance(item, ModelConstraintIR2) for item in all_items),
            requires_quantifiers=scope.kind == "quantifier",
            requires_domains=scope.domain is not None
            or any(a.source == AssumptionSource.DOMAIN for a in assumptions),
            requires_neighborhoods=scope.neighborhood is not None,
            normal_form=normal_form,
        )

    def _iter_literals_or_atoms(self, formula: FormulaIR2) -> Iterable[AtomicIR]:
        if isinstance(formula, NNFFormulaIR2):
            yield from self._iter_atoms_from_logical(formula.expression)
            return

        if isinstance(formula, CNFFormulaIR2):
            for clause in formula.clauses:
                for literal in clause.literals:
                    yield from self._iter_atom_from_literal(literal)
            return

        if isinstance(formula, DNFFormulaIR2):
            for term in formula.terms:
                for literal in term.literals:
                    yield from self._iter_atom_from_literal(literal)
            return

    def _iter_atom_from_literal(self, literal: LiteralIR2) -> Iterable[AtomicIR]:
        yield literal.atom

    def _iter_atoms_from_logical(self, node: LogicalIR) -> Iterable[AtomicIR]:
        if isinstance(node, AtomicIR):
            yield node
            return

        if isinstance(node, NotIR):
            if isinstance(node.operand, AtomicIR):
                yield node.operand
            return

        if isinstance(node, (AndIR, OrIR)):
            for operand in node.operands:
                yield from self._iter_atoms_from_logical(operand)
