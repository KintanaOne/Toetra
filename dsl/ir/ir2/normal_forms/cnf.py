from __future__ import annotations

from dsl.ir.ir1.nodes import AndIR, ComparisonIR, LogicalIR, NotIR, OrIR, ProblemIR
from dsl.ir.ir2.context import IR2BuildContext
from dsl.ir.ir2.enums import Polarity
from dsl.ir.ir2.errors import InvalidNormalFormError, NormalFormExplosionError
from dsl.ir.ir2.nodes import (
    ClauseIR2,
    CNFFormulaIR2,
    LiteralIR2,
    ModelConstraintIR2,
)


class CNFConverter:
    """Converts an NNF logical tree into typed CNFFormulaIR2."""

    def convert(
        self, expr: LogicalIR, context: IR2BuildContext | None = None
    ) -> CNFFormulaIR2:
        context = context or IR2BuildContext()
        cnf = self._to_cnf(expr, context)
        self._check_limit(len(cnf.clauses), context)
        return cnf

    def _to_cnf(self, expr: LogicalIR, context: IR2BuildContext) -> CNFFormulaIR2:
        literal = self._literal_or_none(expr)
        if literal is not None:
            return CNFFormulaIR2(clauses=(ClauseIR2(literals=(literal,)),))

        if isinstance(expr, AndIR):
            clauses: list[ClauseIR2] = []
            for operand in expr.operands:
                clauses.extend(self._to_cnf(operand, context).clauses)
                self._check_limit(len(clauses), context)
            return CNFFormulaIR2(clauses=tuple(clauses))

        if isinstance(expr, OrIR):
            if not expr.operands:
                raise InvalidNormalFormError("Cannot convert empty OrIR to CNF.")

            current = self._to_cnf(expr.operands[0], context)
            for operand in expr.operands[1:]:
                current = self._distribute_or(
                    current, self._to_cnf(operand, context), context
                )
            return current

        raise InvalidNormalFormError(
            f"Unsupported NNF node for CNF conversion: {type(expr).__name__}"
        )

    def _distribute_or(
        self,
        left: CNFFormulaIR2,
        right: CNFFormulaIR2,
        context: IR2BuildContext,
    ) -> CNFFormulaIR2:
        clauses: list[ClauseIR2] = []
        for left_clause in left.clauses:
            for right_clause in right.clauses:
                clauses.append(
                    ClauseIR2(literals=left_clause.literals + right_clause.literals)
                )
                self._check_limit(len(clauses), context)
        return CNFFormulaIR2(clauses=tuple(clauses))

    def _literal_or_none(self, expr: LogicalIR) -> LiteralIR2 | None:
        if isinstance(expr, (ComparisonIR, ProblemIR, ModelConstraintIR2)):
            return LiteralIR2(atom=expr, polarity=Polarity.POSITIVE)

        if isinstance(expr, NotIR):
            if isinstance(
                expr.operand,
                (ComparisonIR, ProblemIR, ModelConstraintIR2),
            ):
                return LiteralIR2(atom=expr.operand, polarity=Polarity.NEGATIVE)
            raise InvalidNormalFormError(
                "CNF conversion expects NNF input; NotIR must wrap an atom."
            )

        return None

    def _check_limit(self, size: int, context: IR2BuildContext) -> None:
        if size > context.max_distribution_size:
            raise NormalFormExplosionError(
                "CNF conversion exceeded "
                f"max_distribution_size={context.max_distribution_size}."
            )
