from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, cast

import z3 as z3_solver

from dsl.backends.capabilities import BackendCapabilities
from dsl.backends.errors import (
    BackendSymbolCollisionError,
    UnsupportedBackendRequirementsError,
    UnsupportedScalarExpressionError,
)
from dsl.backends.z3_backend.capabilities import Z3_CAPABILITIES
from dsl.backends.z3_backend.symbols import (
    Z3LegacyScalarIdentity,
    Z3ModelOutputIdentity,
    Z3ModelQuantityIdentity,
    Z3PointFeatureIdentity,
    Z3SymbolIdentity,
    symbol_identity_metadata,
    z3_symbol_name,
)
from dsl.ir.ir1.model_quantities import ModelQuantityExpressionIR
from dsl.ir.ir1.nodes import (
    AndIR,
    AttributeExpressionIR,
    BinaryArithmeticExpressionIR,
    ComparisonIR,
    ConstantExpressionIR,
    LogicalIR,
    ModelEvaluationIR,
    NotIR,
    OrIR,
    PointBindingIR,
    ProblemIR,
    ScalarExpressionIR,
    SymbolLiteralIR,
    TargetExpressionIR,
    UnaryArithmeticExpressionIR,
)
from dsl.ir.ir2.enums import Polarity
from dsl.ir.ir2.nodes import (
    AffineExpressionIR2,
    AffineModelQuantityConstraintIR2,
    AffineOutputConstraintIR2,
    AffineTermIR2,
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
    symbol_identities: dict[str, Z3SymbolIdentity]

    def identity_for(self, solver_name: str) -> Z3SymbolIdentity:
        """Restore the structured FORML identity for one solver symbol."""

        return self.symbol_identities[solver_name]

    def serialized_symbol_mapping(self) -> dict[str, dict[str, Any]]:
        """Return a JSON-friendly reverse mapping for result construction."""

        return {
            name: symbol_identity_metadata(identity)
            for name, identity in self.symbol_identities.items()
        }


class Z3Translator:
    """Translate the sound numeric affine FORML profile to Z3."""

    backend: EnumBackend = EnumBackend.Z3
    capabilities: BackendCapabilities = Z3_CAPABILITIES

    def __init__(self) -> None:
        self._variables: dict[Z3SymbolIdentity, z3_solver.ArithRef] = {}
        self._symbol_identities: dict[str, Z3SymbolIdentity] = {}
        self._variable_dtypes: dict[Z3SymbolIdentity, EnumDataType] = {}
        self._points_by_name: dict[str, PointBindingIR] = {}
        self._model_evaluations: tuple[ModelEvaluationIR, ...] = ()

    def translate(self, task: VerificationTaskIR2) -> Z3Translation:
        self._reset_symbols()
        self._configure_task_identities(task)
        self._variable_dtypes = self._collect_variable_dtypes(
            task.verification_condition
        )
        self._validate_requirements(task)
        expression = self._translate_formula(task.verification_condition)
        return Z3Translation(
            expression=expression,
            variables=self._variables_by_name(),
            symbol_identities=dict(self._symbol_identities),
        )

    def translate_assumptions(self, task: VerificationTaskIR2) -> Z3Translation:
        """Translate only the aggregated assumptions Γ of a task.

        This secondary translation is used for result diagnostics such as
        vacuity detection. It deliberately excludes the user property and
        therefore answers whether the admissible assumption set itself is
        satisfiable.
        """

        self._reset_symbols()
        self._configure_task_identities(task)
        self._variable_dtypes = self._collect_many_variable_dtypes(
            assumption.formula for assumption in task.assumptions
        )
        expressions = tuple(
            self._translate_formula(assumption.formula)
            for assumption in task.assumptions
        )
        return Z3Translation(
            expression=_bool_and(expressions),
            variables=self._variables_by_name(),
            symbol_identities=dict(self._symbol_identities),
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
        if isinstance(node, AffineModelQuantityConstraintIR2):
            return self._translate_affine_model_quantity_constraint(node)
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
        if isinstance(atom, AffineModelQuantityConstraintIR2):
            return self._translate_affine_model_quantity_constraint(atom)
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
                self._attribute_identity(expression),
                dtype=expression.dtype,
            )
        if isinstance(expression, TargetExpressionIR):
            return self._var(
                self._target_identity(expression),
                dtype=expression.dtype,
            )
        if isinstance(expression, ModelQuantityExpressionIR):
            return self._var(
                self._model_quantity_identity(expression),
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
            self._var(self._affine_output_identity(atom)),
            atom.op,
            self._translate_affine_expression(atom.expression),
        )

    def _translate_affine_model_quantity_constraint(
        self,
        atom: AffineModelQuantityConstraintIR2,
    ) -> z3_solver.BoolRef:
        return self._apply_operator(
            self._var(
                self._model_quantity_identity(atom.quantity),
                dtype=atom.quantity.dtype,
            ),
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
                * self._var(self._affine_term_identity(term)),
            )
        return result

    def _collect_variable_dtypes(
        self,
        formula: FormulaIR2,
    ) -> dict[Z3SymbolIdentity, EnumDataType]:
        return self._collect_many_variable_dtypes((formula,))

    def _collect_many_variable_dtypes(
        self,
        formulas: Iterable[FormulaIR2],
    ) -> dict[Z3SymbolIdentity, EnumDataType]:
        collected: dict[Z3SymbolIdentity, EnumDataType] = {}
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
        collected: dict[Z3SymbolIdentity, EnumDataType],
    ) -> None:
        if not isinstance(
            expression,
            (
                AttributeExpressionIR,
                TargetExpressionIR,
                ModelQuantityExpressionIR,
            ),
        ):
            return
        if expression.dtype is None:
            return
        if expression.dtype not in {EnumDataType.INT, EnumDataType.FLOAT}:
            raise UnsupportedScalarExpressionError(
                f"Z3 numeric profile does not support variable sort "
                f"'{expression.dtype.value}'."
            )
        if isinstance(expression, AttributeExpressionIR):
            identity = self._attribute_identity(expression)
        elif isinstance(expression, TargetExpressionIR):
            identity = self._target_identity(expression)
        else:
            identity = self._model_quantity_identity(expression)
        previous = collected.get(identity)
        if previous is not None and previous is not expression.dtype:
            raise UnsupportedScalarExpressionError(
                f"Conflicting scalar sorts for '{z3_symbol_name(identity)}': "
                f"{previous.value} and {expression.dtype.value}."
            )
        collected[identity] = expression.dtype

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
        if isinstance(
            node,
            (
                ComparisonIR,
                AffineOutputConstraintIR2,
                AffineModelQuantityConstraintIR2,
                ProblemIR,
            ),
        ):
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

    def _reset_symbols(self) -> None:
        self._variables = {}
        self._symbol_identities = {}

    def _variables_by_name(self) -> dict[str, z3_solver.ArithRef]:
        return {
            z3_symbol_name(identity): variable
            for identity, variable in self._variables.items()
        }

    def _attribute_identity(
        self,
        expression: AttributeExpressionIR,
    ) -> Z3SymbolIdentity:
        if expression.point is not None:
            return Z3PointFeatureIdentity(
                point=expression.point,
                feature=expression.feature,
            )
        return self._legacy_feature_identity(
            entity=expression.entity,
            feature=expression.feature,
        )

    def _target_identity(
        self,
        expression: TargetExpressionIR,
    ) -> Z3SymbolIdentity:
        if expression.evaluation is not None:
            return Z3ModelOutputIdentity(evaluation=expression.evaluation)
        return self._legacy_output_identity(
            entity=expression.entity,
            feature=expression.feature,
        )

    @staticmethod
    def _model_quantity_identity(
        expression: ModelQuantityExpressionIR,
    ) -> Z3ModelQuantityIdentity:
        return Z3ModelQuantityIdentity(
            evaluation=expression.evaluation,
            quantity_kind=expression.quantity_kind,
            semantic_profile_id=expression.semantic_profile_id,
        )

    def _affine_output_identity(
        self,
        atom: AffineOutputConstraintIR2,
    ) -> Z3SymbolIdentity:
        if atom.evaluation is not None:
            return Z3ModelOutputIdentity(evaluation=atom.evaluation)
        return self._legacy_output_identity(
            entity=atom.output_entity,
            feature=atom.output_feature,
        )

    def _affine_term_identity(self, term: AffineTermIR2) -> Z3SymbolIdentity:
        if term.point is not None:
            return Z3PointFeatureIdentity(
                point=term.point,
                feature=term.feature,
            )
        return self._legacy_feature_identity(
            entity=term.entity,
            feature=term.feature,
        )

    def _configure_task_identities(self, task: VerificationTaskIR2) -> None:
        points = tuple(mapping.ir_point for mapping in task.point_mappings)
        if not points:
            points = tuple(task.scope.points)
        self._points_by_name = {point.name: point for point in points}
        self._model_evaluations = tuple(task.model_evaluations)

    def _legacy_feature_identity(
        self,
        *,
        entity: str,
        feature: str,
    ) -> Z3SymbolIdentity:
        point = self._points_by_name.get(entity)
        if point is not None:
            return Z3PointFeatureIdentity(point=point, feature=feature)
        return Z3LegacyScalarIdentity(entity=entity, feature=feature)

    def _legacy_output_identity(
        self,
        *,
        entity: str,
        feature: str,
    ) -> Z3SymbolIdentity:
        if entity == "_model":
            candidates = tuple(
                evaluation
                for evaluation in self._model_evaluations
                if evaluation.target_name == feature
            )
            if len(candidates) == 1:
                return Z3ModelOutputIdentity(evaluation=candidates[0])
            if len(candidates) > 1:
                raise UnsupportedScalarExpressionError(
                    "Unindexed legacy model output is ambiguous for multiple "
                    f"evaluations of target {feature!r}."
                )
        return Z3LegacyScalarIdentity(entity=entity, feature=feature)

    def _var(
        self,
        identity: Z3SymbolIdentity,
        *,
        dtype: EnumDataType | None = None,
    ) -> z3_solver.ArithRef:
        if identity not in self._variables:
            name = z3_symbol_name(identity)
            existing_identity = self._symbol_identities.get(name)
            if existing_identity is not None and existing_identity != identity:
                raise BackendSymbolCollisionError(
                    "Distinct FORML identities project to the same Z3 symbol "
                    f"{name!r}: {existing_identity!r} != {identity!r}."
                )

            resolved_dtype = self._variable_dtypes.get(identity, dtype)
            if resolved_dtype is EnumDataType.INT:
                variable = z3_solver.Int(name)
            elif resolved_dtype is None or resolved_dtype is EnumDataType.FLOAT:
                variable = z3_solver.Real(name)
            else:
                raise UnsupportedScalarExpressionError(
                    f"Z3 numeric profile does not support variable sort "
                    f"'{resolved_dtype.value}' for '{name}'."
                )
            self._variables[identity] = cast(z3_solver.ArithRef, variable)
            self._symbol_identities[name] = identity
        return self._variables[identity]

    def _constant(self, value: Any) -> z3_solver.ArithRef:
        if isinstance(value, bool):
            raise UnsupportedScalarExpressionError(
                "Z3 numeric profile does not support boolean constants."
            )
        if isinstance(value, int):
            return cast(z3_solver.ArithRef, z3_solver.IntVal(value))
        if isinstance(value, float):
            return cast(z3_solver.ArithRef, z3_solver.RealVal(str(value)))
        if isinstance(value, Decimal):
            return cast(
                z3_solver.ArithRef,
                z3_solver.RealVal(format(value, "f")),
            )
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
