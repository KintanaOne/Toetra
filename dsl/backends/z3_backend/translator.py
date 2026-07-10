from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, cast

import z3 as z3_solver

from dsl.backends.capabilities import BackendCapabilities
from dsl.backends.z3_backend.capabilities import Z3_CAPABILITIES
from dsl.ir.ir1.nodes import AndIR, ComparisonIR, LogicalIR, NotIR, OrIR, ProblemIR
from dsl.ir.ir2.enums import Polarity
from dsl.ir.ir2.nodes import (
    AffineExpressionIR2,
    AffineOutputConstraintIR2,
    AtomIR2,
    CNFFormulaIR2,
    DNFFormulaIR2,
    FormulaIR2,
    LiteralIR2,
    NNFFormulaIR2,
    VerificationTaskIR2,
)
from dsl.language.vocabulary.backends import EnumBackend
from dsl.language.vocabulary.operators import EnumComparisonOperator


def _bool_and(expressions: Iterable[z3_solver.BoolRef]) -> z3_solver.BoolRef:
    items = tuple(expressions)

    if not items:
        return cast(z3_solver.BoolRef, z3_solver.BoolVal(True))

    return cast(z3_solver.BoolRef, z3_solver.And(*items))


def _bool_or(expressions: Iterable[z3_solver.BoolRef]) -> z3_solver.BoolRef:
    items = tuple(expressions)

    if not items:
        return cast(z3_solver.BoolRef, z3_solver.BoolVal(False))

    return cast(z3_solver.BoolRef, z3_solver.Or(*items))


def _bool_not(expression: z3_solver.BoolRef) -> z3_solver.BoolRef:
    return cast(z3_solver.BoolRef, z3_solver.Not(expression))


@dataclass(frozen=True)
class Z3Translation:
    expression: z3_solver.BoolRef
    variables: dict[str, z3_solver.ArithRef]


class Z3Translator:
    backend: EnumBackend = EnumBackend.Z3
    capabilities: BackendCapabilities = Z3_CAPABILITIES

    def __init__(self) -> None:
        self._variables: dict[str, z3_solver.ArithRef] = {}

    def translate(self, task: VerificationTaskIR2) -> Z3Translation:
        self._variables = {}
        expression = self._translate_formula(task.verification_condition)

        return Z3Translation(
            expression=expression,
            variables=dict(self._variables),
        )

    def _translate_formula(self, formula: FormulaIR2) -> z3_solver.BoolRef:
        if isinstance(formula, NNFFormulaIR2):
            return self._translate_logical(formula.expression)

        if isinstance(formula, CNFFormulaIR2):
            return _bool_and(
                _bool_or(
                    self._translate_literal(literal) for literal in clause.literals
                )
                for clause in formula.clauses
            )

        if isinstance(formula, DNFFormulaIR2):
            return _bool_or(
                _bool_and(self._translate_literal(literal) for literal in term.literals)
                for term in formula.terms
            )

        raise TypeError(f"Unsupported IR2 formula: {type(formula).__name__}")

    def _translate_logical(self, node: LogicalIR) -> z3_solver.BoolRef:
        if isinstance(node, ComparisonIR):
            return self._translate_comparison(node)

        if isinstance(node, AffineOutputConstraintIR2):
            return self._translate_affine_output_constraint(node)

        if isinstance(node, ProblemIR):
            raise NotImplementedError(
                "ProblemIR is not supported by minimal Z3 backend."
            )

        if isinstance(node, AndIR):
            return _bool_and(self._translate_logical(op) for op in node.operands)

        if isinstance(node, OrIR):
            return _bool_or(self._translate_logical(op) for op in node.operands)

        if isinstance(node, NotIR):
            return _bool_not(self._translate_logical(node.operand))

        raise TypeError(f"Unsupported logical IR node: {type(node).__name__}")

    def _translate_literal(self, literal: LiteralIR2) -> z3_solver.BoolRef:
        atom = self._translate_atom(literal.atom)

        if literal.polarity == Polarity.POSITIVE:
            return atom

        if literal.polarity == Polarity.NEGATIVE:
            return _bool_not(atom)

        raise ValueError(f"Unsupported literal polarity: {literal.polarity}")

    def _translate_atom(self, atom: AtomIR2) -> z3_solver.BoolRef:
        if isinstance(atom, ComparisonIR):
            return self._translate_comparison(atom)

        if isinstance(atom, AffineOutputConstraintIR2):
            return self._translate_affine_output_constraint(atom)

        if isinstance(atom, ProblemIR):
            raise NotImplementedError(
                "ProblemIR is not supported by minimal Z3 backend."
            )

        raise TypeError(f"Unsupported atom: {type(atom).__name__}")

    def _translate_comparison(self, atom: ComparisonIR) -> z3_solver.BoolRef:
        left = self._var(atom.entity, atom.feature)
        right = self._constant(atom.value)

        return self._apply_operator(left, atom.op, right)

    def _translate_affine_output_constraint(
        self,
        atom: AffineOutputConstraintIR2,
    ) -> z3_solver.BoolRef:
        left = self._var(atom.output_entity, atom.output_feature)
        right = self._translate_affine_expression(atom.expression)

        return self._apply_operator(left, atom.op, right)

    def _translate_affine_expression(
        self,
        expression: AffineExpressionIR2,
    ) -> z3_solver.ArithRef:
        result = cast(z3_solver.ArithRef, z3_solver.RealVal(expression.bias))

        for term in expression.terms:
            coefficient = cast(
                z3_solver.ArithRef,
                z3_solver.RealVal(term.coefficient),
            )
            variable = self._var(term.entity, term.feature)
            result = cast(z3_solver.ArithRef, result + coefficient * variable)

        return result

    def _var(self, entity: str, feature: str) -> z3_solver.ArithRef:
        name = f"{entity}.{feature}"

        if name not in self._variables:
            self._variables[name] = cast(z3_solver.ArithRef, z3_solver.Real(name))

        return self._variables[name]

    def _constant(self, value: Any) -> z3_solver.ArithRef:
        if isinstance(value, bool):
            raise TypeError(
                "Boolean constants are not supported in numeric comparisons."
            )

        if isinstance(value, int):
            return cast(z3_solver.ArithRef, z3_solver.IntVal(value))

        if isinstance(value, float):
            return cast(z3_solver.ArithRef, z3_solver.RealVal(value))

        raise TypeError(f"Unsupported comparison constant: {value!r}")

    def _apply_operator(
        self,
        left: z3_solver.ArithRef,
        op: EnumComparisonOperator,
        right: z3_solver.ArithRef,
    ) -> z3_solver.BoolRef:
        if op == EnumComparisonOperator.EQ:
            return cast(z3_solver.BoolRef, left == right)

        if op == EnumComparisonOperator.NEQ:
            return cast(z3_solver.BoolRef, left != right)

        if op == EnumComparisonOperator.LT:
            return cast(z3_solver.BoolRef, left < right)

        if op == EnumComparisonOperator.LTE:
            return cast(z3_solver.BoolRef, left <= right)

        if op == EnumComparisonOperator.GT:
            return cast(z3_solver.BoolRef, left > right)

        if op == EnumComparisonOperator.GTE:
            return cast(z3_solver.BoolRef, left >= right)

        raise ValueError(f"Unsupported comparison operator: {op}")
