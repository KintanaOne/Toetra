from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Any, cast

import z3 as z3_solver

from dsl.backends.capabilities import BackendCapabilities
from dsl.backends.errors import (
    UnsupportedBackendRequirementsError,
    UnsupportedScalarExpressionError,
)
from dsl.backends.z3_backend.capabilities import Z3_CAPABILITIES
from dsl.ir.ir1.nodes import (
    AndIR,
    AttributeExpressionIR,
    BinaryArithmeticExpressionIR,
    ComparisonIR,
    ConstantExpressionIR,
    LogicalIR,
    NotIR,
    OrIR,
    ProblemIR,
    ScalarExpressionIR,
    SymbolLiteralIR,
    TargetExpressionIR,
    UnaryArithmeticExpressionIR,
)
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
from dsl.language.vocabulary.operators import (
    EnumArithmeticOperator,
    EnumComparisonOperator,
    EnumUnaryOperator,
)
from dsl.semantic.types.enums import EnumDataType


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
    """Translate the sound numeric affine FORML profile to Z3."""

    backend: EnumBackend = EnumBackend.Z3
    capabilities: BackendCapabilities = Z3_CAPABILITIES

    def __init__(self) -> None:
        self._variables: dict[str, z3_solver.ArithRef] = {}
        self._variable_dtypes: dict[str, EnumDataType] = {}

    def translate(self, task: VerificationTaskIR2) -> Z3Translation:
        self._variables = {}
        self._variable_dtypes = self._collect_variable_dtypes(
            task.verification_condition
        )
        self._validate_requirements(task)
        expression = self._translate_formula(task.verification_condition)
        return Z3Translation(
            expression=expression,
            variables=dict(self._variables),
        )

    def translate_assumptions(self, task: VerificationTaskIR2) -> Z3Translation:
        """Translate only the aggregated assumptions Γ of a task.

        This secondary translation is used for result diagnostics such as
        vacuity detection. It deliberately excludes the user property and
        therefore answers whether the admissible assumption set itself is
        satisfiable.
        """

        self._variables = {}
        self._variable_dtypes = self._collect_many_variable_dtypes(
            assumption.formula for assumption in task.assumptions
        )
        expressions = tuple(
            self._translate_formula(assumption.formula)
            for assumption in task.assumptions
        )
        return Z3Translation(
            expression=_bool_and(expressions),
            variables=dict(self._variables),
        )

    def _validate_requirements(self, task: VerificationTaskIR2) -> None:
        incompatibilities = self.capabilities.incompatibilities(task.requirements)
        if not incompatibilities:
            return
        details = "; ".join(incompatibilities)
        raise UnsupportedBackendRequirementsError(
            f"Z3 does not satisfy IR2 requirements: {details}"
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
            raise NotImplementedError("ProblemIR is not supported by the Z3 backend.")
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
            raise NotImplementedError("ProblemIR is not supported by the Z3 backend.")
        raise TypeError(f"Unsupported atom: {type(atom).__name__}")

    def _translate_comparison(self, atom: ComparisonIR) -> z3_solver.BoolRef:
        return self._apply_operator(
            self._translate_scalar(atom.left),
            atom.op,
            self._translate_scalar(atom.right),
        )

    def _translate_scalar(self, expression: ScalarExpressionIR) -> z3_solver.ArithRef:
        if isinstance(expression, AttributeExpressionIR):
            return self._var(
                expression.entity,
                expression.feature,
                dtype=expression.dtype,
            )
        if isinstance(expression, TargetExpressionIR):
            return self._var(
                expression.entity,
                expression.feature,
                dtype=expression.dtype,
            )
        if isinstance(expression, ConstantExpressionIR):
            return self._constant(expression.value)
        if isinstance(expression, SymbolLiteralIR):
            raise UnsupportedScalarExpressionError(
                f"Z3 numeric profile does not support symbolic category "
                f"{expression.name!r}."
            )
        if isinstance(expression, UnaryArithmeticExpressionIR):
            operand = self._translate_scalar(expression.operand)
            if expression.operator is EnumUnaryOperator.PLUS:
                return operand
            if expression.operator is EnumUnaryOperator.MINUS:
                return cast(z3_solver.ArithRef, -operand)
            raise UnsupportedScalarExpressionError(
                f"Unsupported unary operator: {expression.operator.value}"
            )
        if isinstance(expression, BinaryArithmeticExpressionIR):
            return self._translate_binary_arithmetic(expression)
        raise TypeError(
            f"Unsupported scalar IR expression: {type(expression).__name__}"
        )

    def _translate_binary_arithmetic(
        self,
        expression: BinaryArithmeticExpressionIR,
    ) -> z3_solver.ArithRef:
        operator = expression.operator
        if operator is EnumArithmeticOperator.ADD:
            return cast(
                z3_solver.ArithRef,
                self._translate_scalar(expression.left)
                + self._translate_scalar(expression.right),
            )
        if operator is EnumArithmeticOperator.SUB:
            return cast(
                z3_solver.ArithRef,
                self._translate_scalar(expression.left)
                - self._translate_scalar(expression.right),
            )
        if operator is EnumArithmeticOperator.MUL:
            left_constant = self._numeric_constant_value(expression.left)
            right_constant = self._numeric_constant_value(expression.right)
            if left_constant is not None:
                return cast(
                    z3_solver.ArithRef,
                    self._constant(left_constant)
                    * self._translate_scalar(expression.right),
                )
            if right_constant is not None:
                return cast(
                    z3_solver.ArithRef,
                    self._translate_scalar(expression.left)
                    * self._constant(right_constant),
                )
            raise UnsupportedScalarExpressionError(
                "Z3 affine profile rejects nonlinear multiplication between "
                "two symbolic expressions."
            )
        if operator is EnumArithmeticOperator.DIV:
            denominator = self._numeric_constant_value(expression.right)
            if denominator is None:
                raise UnsupportedScalarExpressionError(
                    "Z3 affine profile rejects division by a symbolic expression."
                )
            if denominator == 0:
                raise UnsupportedScalarExpressionError(
                    "Z3 affine profile rejects division by zero."
                )
            return cast(
                z3_solver.ArithRef,
                self._translate_scalar(expression.left) / self._constant(denominator),
            )
        raise UnsupportedScalarExpressionError(
            f"Unsupported arithmetic operator: {operator.value}"
        )

    def _numeric_constant_value(
        self,
        expression: ScalarExpressionIR,
    ) -> int | float | None:
        if isinstance(expression, ConstantExpressionIR):
            value = expression.value
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return None
            return value
        if isinstance(expression, UnaryArithmeticExpressionIR):
            operand = self._numeric_constant_value(expression.operand)
            if operand is None:
                return None
            if expression.operator is EnumUnaryOperator.PLUS:
                return +operand
            if expression.operator is EnumUnaryOperator.MINUS:
                return -operand
            return None
        if not isinstance(expression, BinaryArithmeticExpressionIR):
            return None
        left = self._numeric_constant_value(expression.left)
        right = self._numeric_constant_value(expression.right)
        if left is None or right is None:
            return None
        if expression.operator is EnumArithmeticOperator.ADD:
            return left + right
        if expression.operator is EnumArithmeticOperator.SUB:
            return left - right
        if expression.operator is EnumArithmeticOperator.MUL:
            return left * right
        if expression.operator is EnumArithmeticOperator.DIV:
            if right == 0:
                raise UnsupportedScalarExpressionError(
                    "Z3 affine profile rejects division by zero."
                )
            return left / right
        return None

    def _translate_affine_output_constraint(
        self,
        atom: AffineOutputConstraintIR2,
    ) -> z3_solver.BoolRef:
        return self._apply_operator(
            self._var(atom.output_entity, atom.output_feature),
            atom.op,
            self._translate_affine_expression(atom.expression),
        )

    def _translate_affine_expression(
        self,
        expression: AffineExpressionIR2,
    ) -> z3_solver.ArithRef:
        result = self._constant(expression.bias)
        for term in expression.terms:
            result = cast(
                z3_solver.ArithRef,
                result
                + self._constant(term.coefficient)
                * self._var(term.entity, term.feature),
            )
        return result

    def _collect_variable_dtypes(
        self,
        formula: FormulaIR2,
    ) -> dict[str, EnumDataType]:
        return self._collect_many_variable_dtypes((formula,))

    def _collect_many_variable_dtypes(
        self,
        formulas: Iterable[FormulaIR2],
    ) -> dict[str, EnumDataType]:
        collected: dict[str, EnumDataType] = {}
        for formula in formulas:
            for atom in self._iter_formula_atoms(formula):
                if not isinstance(atom, ComparisonIR):
                    continue
                for expression in self._iter_scalar_tree(atom.left):
                    self._record_expression_dtype(expression, collected)
                for expression in self._iter_scalar_tree(atom.right):
                    self._record_expression_dtype(expression, collected)
        return collected

    def _record_expression_dtype(
        self,
        expression: ScalarExpressionIR,
        collected: dict[str, EnumDataType],
    ) -> None:
        if not isinstance(
            expression,
            (AttributeExpressionIR, TargetExpressionIR),
        ):
            return
        if expression.dtype is None:
            return
        if expression.dtype not in {EnumDataType.INT, EnumDataType.FLOAT}:
            raise UnsupportedScalarExpressionError(
                f"Z3 numeric profile does not support variable sort "
                f"'{expression.dtype.value}'."
            )
        name = f"{expression.entity}.{expression.feature}"
        previous = collected.get(name)
        if previous is not None and previous is not expression.dtype:
            raise UnsupportedScalarExpressionError(
                f"Conflicting scalar sorts for '{name}': "
                f"{previous.value} and {expression.dtype.value}."
            )
        collected[name] = expression.dtype

    def _iter_formula_atoms(self, formula: FormulaIR2) -> Iterator[AtomIR2]:
        if isinstance(formula, NNFFormulaIR2):
            yield from self._iter_logical_atoms(formula.expression)
            return
        if isinstance(formula, CNFFormulaIR2):
            for clause in formula.clauses:
                for literal in clause.literals:
                    yield literal.atom
            return
        if isinstance(formula, DNFFormulaIR2):
            for term in formula.terms:
                for literal in term.literals:
                    yield literal.atom
            return
        raise TypeError(f"Unsupported IR2 formula: {type(formula).__name__}")

    def _iter_logical_atoms(self, node: LogicalIR) -> Iterator[AtomIR2]:
        if isinstance(node, (ComparisonIR, AffineOutputConstraintIR2, ProblemIR)):
            yield node
            return
        if isinstance(node, (AndIR, OrIR)):
            for operand in node.operands:
                yield from self._iter_logical_atoms(operand)
            return
        if isinstance(node, NotIR):
            yield from self._iter_logical_atoms(node.operand)
            return
        raise TypeError(f"Unsupported logical IR node: {type(node).__name__}")

    def _iter_scalar_tree(
        self,
        expression: ScalarExpressionIR,
    ) -> Iterator[ScalarExpressionIR]:
        yield expression
        if isinstance(expression, UnaryArithmeticExpressionIR):
            yield from self._iter_scalar_tree(expression.operand)
            return
        if isinstance(expression, BinaryArithmeticExpressionIR):
            yield from self._iter_scalar_tree(expression.left)
            yield from self._iter_scalar_tree(expression.right)

    def _var(
        self,
        entity: str,
        feature: str,
        *,
        dtype: EnumDataType | None = None,
    ) -> z3_solver.ArithRef:
        name = f"{entity}.{feature}"
        if name not in self._variables:
            resolved_dtype = self._variable_dtypes.get(name, dtype)
            if resolved_dtype is EnumDataType.INT:
                variable = z3_solver.Int(name)
            elif resolved_dtype is None or resolved_dtype is EnumDataType.FLOAT:
                variable = z3_solver.Real(name)
            else:
                raise UnsupportedScalarExpressionError(
                    f"Z3 numeric profile does not support variable sort "
                    f"'{resolved_dtype.value}' for '{name}'."
                )
            self._variables[name] = cast(z3_solver.ArithRef, variable)
        return self._variables[name]

    def _constant(self, value: Any) -> z3_solver.ArithRef:
        if isinstance(value, bool):
            raise UnsupportedScalarExpressionError(
                "Z3 numeric profile does not support boolean constants."
            )
        if isinstance(value, int):
            return cast(z3_solver.ArithRef, z3_solver.IntVal(value))
        if isinstance(value, float):
            return cast(z3_solver.ArithRef, z3_solver.RealVal(str(value)))
        raise UnsupportedScalarExpressionError(
            f"Z3 numeric profile does not support scalar constant {value!r}."
        )

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
