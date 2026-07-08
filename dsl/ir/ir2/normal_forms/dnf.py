from __future__ import annotations

from dsl.ir.ir1.nodes import AndIR, AtomicIR, LogicalIR, NotIR, OrIR
from dsl.ir.ir2.context import IR2BuildContext
from dsl.ir.ir2.dsl.nodes import DNFFormulaIR2, LiteralIR2, TermIR2
from dsl.ir.ir2.enums import Polarity
from dsl.ir.ir2.errors import InvalidNormalFormError, NormalFormExplosionError


class DNFConverter:
    """Converts an NNF logical tree into typed DNFFormulaIR2."""

    def convert(
        self, expr: LogicalIR, context: IR2BuildContext | None = None
    ) -> DNFFormulaIR2:
        context = context or IR2BuildContext()
        dnf = self._to_dnf(expr, context)
        self._check_limit(len(dnf.terms), context)
        return dnf

    def _to_dnf(self, expr: LogicalIR, context: IR2BuildContext) -> DNFFormulaIR2:
        literal = self._literal_or_none(expr)
        if literal is not None:
            return DNFFormulaIR2(terms=(TermIR2(literals=(literal,)),))

        if isinstance(expr, OrIR):
            terms: list[TermIR2] = []
            for operand in expr.operands:
                terms.extend(self._to_dnf(operand, context).terms)
                self._check_limit(len(terms), context)
            return DNFFormulaIR2(terms=tuple(terms))

        if isinstance(expr, AndIR):
            if not expr.operands:
                raise InvalidNormalFormError("Cannot convert empty AndIR to DNF.")

            current = self._to_dnf(expr.operands[0], context)
            for operand in expr.operands[1:]:
                current = self._distribute_and(
                    current, self._to_dnf(operand, context), context
                )
            return current

        raise InvalidNormalFormError(
            f"Unsupported NNF node for DNF conversion: {type(expr).__name__}"
        )

    def _distribute_and(
        self,
        left: DNFFormulaIR2,
        right: DNFFormulaIR2,
        context: IR2BuildContext,
    ) -> DNFFormulaIR2:
        terms: list[TermIR2] = []
        for left_term in left.terms:
            for right_term in right.terms:
                terms.append(TermIR2(literals=left_term.literals + right_term.literals))
                self._check_limit(len(terms), context)
        return DNFFormulaIR2(terms=tuple(terms))

    def _literal_or_none(self, expr: LogicalIR) -> LiteralIR2 | None:
        if isinstance(expr, AtomicIR):
            return LiteralIR2(atom=expr, polarity=Polarity.POSITIVE)

        if isinstance(expr, NotIR):
            if isinstance(expr.operand, AtomicIR):
                return LiteralIR2(atom=expr.operand, polarity=Polarity.NEGATIVE)
            raise InvalidNormalFormError(
                "DNF conversion expects NNF input; NotIR must wrap an atom."
            )

        return None

    def _check_limit(self, size: int, context: IR2BuildContext) -> None:
        if size > context.max_distribution_size:
            raise NormalFormExplosionError(
                "DNF conversion exceeded "
                f"max_distribution_size={context.max_distribution_size}."
            )
