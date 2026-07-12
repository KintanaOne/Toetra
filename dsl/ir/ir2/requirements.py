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
from dsl.ir.ir2.enums import (
    AssumptionSource,
    NormalFormKind,
    VerificationSemantics,
)
from dsl.ir.ir2.model.affine import AffineOutputConstraintIR2
from dsl.ir.ir2.model.base import ModelConstraintIR2


@dataclass(frozen=True)
class IR2Requirements:
    """Backend-neutral capabilities required by a VerificationTaskIR2.

    Important distinction
    ---------------------
    ``uses_quantified_scope`` describes the original FORML specification.

    ``requires_native_quantifiers`` describes the representation that reaches
    the backend after IR2 lowering.

    A specification such as::

        forall x0 => P(x0)

    uses a quantified scope, but it does not require native backend
    quantifiers when FORML lowers it to the refutation condition::

        Γ(x0) AND NOT P(x0)

    ``requires_quantifiers`` is temporarily retained as a compatibility field.
    During the migration it represents the same backend requirement as
    ``requires_native_quantifiers``. It will be removed once all callers and
    backend capabilities use the explicit native-quantifier field.
    """

    requires_boolean_logic: bool
    requires_numeric_comparisons: bool
    requires_problem_predicates: bool
    requires_model_assertions: bool

    # Temporary compatibility field.
    requires_quantifiers: bool

    requires_domains: bool
    requires_neighborhoods: bool
    normal_form: NormalFormKind

    # New explicit contract.
    uses_quantified_scope: bool = False
    requires_native_quantifiers: bool = False
    required_verification_semantics: VerificationSemantics = (
        VerificationSemantics.REFUTATION
    )


class RequirementsAnalyzer:
    """Compute backend requirements from an already lowered IR2 task.

    The analyzer must describe what the backend actually receives, not merely
    reproduce the syntax originally written by the user.
    """

    def analyze(
        self,
        *,
        scope: ScopeIR,
        verification_condition: FormulaIR2,
        assumptions: tuple[AssumptionIR2, ...],
        normal_form: NormalFormKind,
        semantics: VerificationSemantics = VerificationSemantics.REFUTATION,
        requires_native_quantifiers: bool = False,
    ) -> IR2Requirements:
        literals = list(self._iter_literals_or_atoms(verification_condition))

        assumption_literals: list[AtomicIR] = []
        for assumption in assumptions:
            assumption_literals.extend(self._iter_literals_or_atoms(assumption.formula))

        all_items = literals + assumption_literals
        uses_quantified_scope = scope.kind == "quantifier"

        return IR2Requirements(
            requires_boolean_logic=True,
            requires_numeric_comparisons=any(
                isinstance(
                    item,
                    (
                        ComparisonIR,
                        AffineOutputConstraintIR2,
                    ),
                )
                for item in all_items
            ),
            requires_problem_predicates=any(
                isinstance(item, ProblemIR) for item in all_items
            ),
            requires_model_assertions=any(
                assumption.source == AssumptionSource.MODEL
                for assumption in assumptions
            )
            or any(isinstance(item, ModelConstraintIR2) for item in all_items),
            # Compatibility field: it now reflects a backend-native need,
            # not the mere presence of a quantified FORML scope.
            requires_quantifiers=requires_native_quantifiers,
            requires_domains=scope.domain is not None
            or any(
                assumption.source == AssumptionSource.DOMAIN
                for assumption in assumptions
            ),
            requires_neighborhoods=scope.neighborhood is not None,
            normal_form=normal_form,
            # New explicit information.
            uses_quantified_scope=uses_quantified_scope,
            requires_native_quantifiers=requires_native_quantifiers,
            required_verification_semantics=semantics,
        )

    def _iter_literals_or_atoms(
        self,
        formula: FormulaIR2,
    ) -> Iterable[AtomicIR]:
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

        raise TypeError(f"Unsupported IR2 formula type: {type(formula).__name__}")

    def _iter_atom_from_literal(
        self,
        literal: LiteralIR2,
    ) -> Iterable[AtomicIR]:
        yield literal.atom

    def _iter_atoms_from_logical(
        self,
        node: LogicalIR,
    ) -> Iterable[AtomicIR]:
        if isinstance(node, AtomicIR):
            yield node
            return

        if isinstance(node, NotIR):
            if isinstance(node.operand, AtomicIR):
                yield node.operand
                return

            yield from self._iter_atoms_from_logical(node.operand)
            return

        if isinstance(node, (AndIR, OrIR)):
            for operand in node.operands:
                yield from self._iter_atoms_from_logical(operand)
            return

        raise TypeError(
            f"Unsupported logical IR node while computing requirements: "
            f"{type(node).__name__}"
        )
