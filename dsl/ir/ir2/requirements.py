from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from dsl.ir.ir1.nodes import (
    AndIR,
    AtomicIR,
    AttributeExpressionIR,
    BinaryArithmeticExpressionIR,
    ComparisonIR,
    ConstantExpressionIR,
    LogicalIR,
    NotIR,
    OrIR,
    ProblemIR,
    ScalarExpressionIR,
    ScopeIR,
    SymbolLiteralIR,
    TargetExpressionIR,
    UnaryArithmeticExpressionIR,
)
from dsl.ir.ir1.scalar import iter_scalar_expressions
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
from dsl.language.vocabulary.operators import EnumArithmeticOperator
from dsl.semantic.types.enums import EnumArithmeticClass, EnumDataType


@dataclass(frozen=True)
class IR2Requirements:
    """Backend-neutral capabilities required by a VerificationTaskIR2.

    The legacy coarse flags remain available for compatibility. The additional
    scalar/domain fields expose the distinctions required by typed domains and
    recursive arithmetic before backend capability matching is upgraded.
    """

    requires_boolean_logic: bool
    requires_numeric_comparisons: bool
    requires_problem_predicates: bool
    requires_model_assertions: bool

    requires_domains: bool
    requires_neighborhoods: bool
    normal_form: NormalFormKind

    uses_quantified_scope: bool = False
    requires_native_quantifiers: bool = False
    required_verification_semantics: VerificationSemantics = (
        VerificationSemantics.REFUTATION
    )

    requires_affine_arithmetic: bool = False
    requires_nonlinear_arithmetic: bool = False
    requires_symbolic_division: bool = False
    required_scalar_sorts: frozenset[EnumDataType] = frozenset()
    requires_finite_set_membership: bool = False
    requires_symbolic_categories: bool = False
    requires_domain_assumptions: bool = False


class RequirementsAnalyzer:
    """Compute backend requirements from an already lowered IR2 task.

    Requirements describe what reaches the backend after domain/model
    assumptions have been aggregated. They never select a backend and never
    rewrite unsupported arithmetic silently.
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
        atoms = list(self._iter_literals_or_atoms(verification_condition))

        assumption_atoms: list[AtomicIR] = []
        for assumption in assumptions:
            assumption_atoms.extend(self._iter_literals_or_atoms(assumption.formula))

        all_items = atoms + assumption_atoms
        uses_quantified_scope = scope.kind == "quantifier"
        domain_assumptions = tuple(
            assumption
            for assumption in assumptions
            if assumption.source is AssumptionSource.DOMAIN
        )

        scalar_expressions = tuple(self._iter_scalar_expressions(all_items))
        arithmetic_classes = {
            arithmetic_class
            for expression in scalar_expressions
            if (arithmetic_class := self._arithmetic_class(expression)) is not None
        }
        required_scalar_sorts = frozenset(
            dtype
            for expression in scalar_expressions
            if (dtype := self._dtype(expression)) is not None
        )

        requires_symbolic_categories = any(
            isinstance(expression, SymbolLiteralIR) for expression in scalar_expressions
        )
        requires_finite_set_membership = any(
            assumption.metadata.get("constraint_kind") == "finite_set"
            for assumption in domain_assumptions
        )

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
                assumption.source is AssumptionSource.MODEL
                for assumption in assumptions
            )
            or any(isinstance(item, ModelConstraintIR2) for item in all_items),
            requires_domains=scope.domain is not None or bool(domain_assumptions),
            requires_neighborhoods=scope.neighborhood is not None,
            normal_form=normal_form,
            uses_quantified_scope=uses_quantified_scope,
            requires_native_quantifiers=requires_native_quantifiers,
            required_verification_semantics=semantics,
            requires_affine_arithmetic=(
                EnumArithmeticClass.AFFINE in arithmetic_classes
                or any(
                    isinstance(item, AffineOutputConstraintIR2) for item in all_items
                )
            ),
            requires_nonlinear_arithmetic=(
                EnumArithmeticClass.NONLINEAR in arithmetic_classes
            ),
            requires_symbolic_division=(
                EnumArithmeticClass.SYMBOLIC_DIVISION in arithmetic_classes
            ),
            required_scalar_sorts=required_scalar_sorts,
            requires_finite_set_membership=requires_finite_set_membership,
            requires_symbolic_categories=requires_symbolic_categories,
            requires_domain_assumptions=bool(domain_assumptions),
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

    @staticmethod
    def _iter_atom_from_literal(
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
            "Unsupported logical IR node while computing requirements: "
            f"{type(node).__name__}"
        )

    def _iter_scalar_expressions(
        self,
        atoms: Iterable[AtomicIR],
    ) -> Iterable[ScalarExpressionIR]:
        for atom in atoms:
            if isinstance(atom, ComparisonIR):
                yield from iter_scalar_expressions(atom.left)
                yield from iter_scalar_expressions(atom.right)
            elif isinstance(atom, AffineOutputConstraintIR2):
                yield TargetExpressionIR(
                    entity=atom.output_entity,
                    feature=atom.output_feature,
                    dtype=EnumDataType.FLOAT,
                )

    @staticmethod
    def _dtype(expression: ScalarExpressionIR) -> EnumDataType | None:
        if isinstance(expression, ConstantExpressionIR):
            return expression.dtype
        if isinstance(
            expression,
            (
                AttributeExpressionIR,
                TargetExpressionIR,
                UnaryArithmeticExpressionIR,
                BinaryArithmeticExpressionIR,
            ),
        ):
            return expression.dtype
        return None

    def _arithmetic_class(
        self,
        expression: ScalarExpressionIR,
    ) -> EnumArithmeticClass | None:
        if isinstance(expression, UnaryArithmeticExpressionIR):
            return expression.arithmetic_class or EnumArithmeticClass.AFFINE

        if not isinstance(expression, BinaryArithmeticExpressionIR):
            return None

        if expression.arithmetic_class is not None:
            return expression.arithmetic_class

        if expression.operator is EnumArithmeticOperator.DIV:
            if not self._is_constant_expression(expression.right):
                return EnumArithmeticClass.SYMBOLIC_DIVISION
            return EnumArithmeticClass.AFFINE

        if expression.operator is EnumArithmeticOperator.MUL:
            if not (
                self._is_constant_expression(expression.left)
                or self._is_constant_expression(expression.right)
            ):
                return EnumArithmeticClass.NONLINEAR

        return EnumArithmeticClass.AFFINE

    def _is_constant_expression(self, expression: ScalarExpressionIR) -> bool:
        if isinstance(expression, ConstantExpressionIR):
            return True
        if isinstance(expression, UnaryArithmeticExpressionIR):
            return self._is_constant_expression(expression.operand)
        if isinstance(expression, BinaryArithmeticExpressionIR):
            return self._is_constant_expression(
                expression.left
            ) and self._is_constant_expression(expression.right)
        return False
